import asyncio
import json
import logging
import getpass
import datetime
import uuid

from confluent_kafka import Producer, Consumer
from cryptography.fernet import Fernet
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.widgets import RichLog, Input, Header
from tzlocal import get_localzone


# --- This part is to redirect all rdkafka logs to /dev/null ---
chatlogger = logging.getLogger("chat")
chatlogger.addHandler(logging.NullHandler())
# --------------------------------------------------------------

# Get the system's local time zone
_local_tz = get_localzone()


class History(RichLog):
    auto_scroll = True


class ChatWithKafkaApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "Chat With Kafka"
    SUB_TITLE = "Chat TUI using Kafka!"

    def __init__(self, kafkaconf, topic, symmetric_key=None, user=None):
        super().__init__()
        # Store config values
        self._kafkaconf = kafkaconf
        self._topic = topic
        self._f = Fernet(symmetric_key) if symmetric_key else None
        self._user = user if user else getpass.getuser()

        # Create the consumer and producer variables
        self.consumer = None
        self.producer = None

    def compose(self) -> ComposeResult:
        """This is where we define the components of the app.

        The styling of the app is specified in the app.tcss file.
        """
        yield Header(id="header")
        yield RichLog(id="history", markup=True, auto_scroll=True)
        yield Input(id="message")

    def on_mount(self) -> None:
        """This is run when all initial layout and rendering has been done. This is the perfect
        place to start the consumer and create the producer."""
        # Create the consumer
        grp = str(uuid.uuid4())
        self.consumer = Consumer(
            {**self._kafkaconf, **{"group.id": grp, "auto.offset.reset": "earliest"}}, logger=chatlogger
        )
        self.consumer.subscribe([self._topic])
        # Run the consumer in a separate thread, as a async worker.
        self.run_worker(self.update_history(), exclusive=False)

        # Create the producer
        self.producer = Producer(self._kafkaconf, logger=chatlogger)
        # Set focus to the input field, so the user can type messages right away.
        self.query("#message").focus()
        # Also, send info about that the user has entered the chat.
        self._send_message("Has entered the chat.")

    def _send_message(self, message: str):
        """Send a message to a topic with the previously created producer."""
        # We package this as a JSON message with the user, the message, and the time.
        # This is to be able to ensure that the time is sent as UTC time and not local time,
        # which is what is present in the msg.timestamp() method...
        # If we used the app outside the Europe/Stockholm timezone, then we would have problems
        # knowing when the message was sent for that user...
        msg = {
            "message": message if (self._f is None) else self._f.encrypt(message.encode("utf-8")).decode("utf-8"),
            "user": self._user,
            "time": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        }
        self.query("#history").first().write(str(msg))
        self.producer.produce("chat", key=self._user, value=json.dumps(msg))
        self.producer.flush()

    async def update_history(self):
        while True:
            # We have to first poll a short while to get the messages and then sleep in an async/await way
            # to allow the main thread to update the history on the screen.
            msg = self.consumer.poll(0.05)
            await asyncio.sleep(0.05)
            if not msg:
                continue
            elif msg.error():
                self.query("#history").first().write(f"Consumer error: {msg.error()}")
                print(f"Consumer error: {msg.error()}")
                break
            else:
                try:
                    # First, deserialize the message from JSON
                    message = json.loads(msg.value().decode("utf-8"))
                    # Now, parse the time string and the convert it from UTC to the local timezone,
                    # i.e. the one that the system's locale is set to.
                    # For this we use the tzlocal package.
                    local_time = datetime.datetime.fromisoformat(message["time"]).astimezone(_local_tz)
                    # Also convert it to nice string format.
                    local_time = local_time.strftime("%Y-%m-%d %H:%M:%S.%f")

                    # Now try to decrypt the message text if we have a key.
                    if self._f:
                        try:
                            msg_text = self._f.decrypt(message["message"]).decode("utf-8")
                        except Exception as e:
                            self.query("#history").first().write(str(e))
                            msg_text = f"[red][Error decoding message][/red] {message['message']}"
                    else:
                        msg_text = message["message"]

                    self.query("#history").first().write(f'[red]{local_time}[/red] [white]{message["user"]}[/white]: {msg_text}')
                except:
                    self.query("#history").first().write(f"Error decoding message: {msg.value().decode('utf-8')}")
                self.query("#history").first().refresh()

    def on_key(self, event: Key):
        """This is the event handler for key events. We use this to handle the enter key and the escape key."""
        if event.key == "escape":
            self.exit()
        elif event.key == "enter":
            input = self.query("#message").first()
            message = input.value
            self.log("Sending message: " + message)
            self._send_message(message)
            input.value = ""
            input.refresh()

    def _on_exit_app(self) -> None:
        self._send_message("Has left the chat.")
