import json
from argparse import ArgumentParser
import pathlib

from chatwithkafka.app import ChatWithKafkaApp


def cli():
    """Command line interface for the chat with Kafka app"""

    parser = ArgumentParser(description="Chat Terminal User Interface (TUI) with Kafka")

    parser.add_argument(
        "config_file",
        help="Path to the JSON configuration file"
    )
    parser.add_argument(
        "-u",
        "--user",
        help="User name to use in chat. If none is provided, the currently logged in user's name will be used",
    )
    parser.add_argument(
        "-t",
        "--topic",
        default=None,
        help="Topic to use for chat. Overrides the topic in the configuration file"
    )
    parser.add_argument(
        "--key",
        default=None,
        help="Symmetric Fernet key to use encrypting and decrypting messages. Overrides the key in the configuration file",
    )

    args = parser.parse_args()
    config_path = pathlib.Path(args.config_file).resolve()
    if not config_path.exists():
        print(f"Error: Configuration file {config_path} does not exist")
        return
    with config_path.open("rt") as f:
        config = json.load(f)

    topic = args.topic if args.topic else config.get("topic")
    key = args.key if args.key else config.get("symmetric_key")

    app = ChatWithKafkaApp(config.get("kafkaconf"), topic, symmetric_key=key, user=args.user)
    app.run()


if __name__ == "__main__":
    cli()
