# Chat With Kafka

This is a simple chat application that uses Kafka as a 
message broker. The application is written in Python and
uses the `confluent-kafka` library to interact with Kafka
and the [`textual`](https://textual.textualize.io/) framework 
to create the chat interface in the terminal.

It was written as demonstration of how to use Kafka to
create a chat application for a project course at
Karlstad University.

## Installation

To install the application you type

```powershell
pip install chatwithkafka
```

It can also be installed from the source code by cloning
the repository and running

```powershell
pip install .
```

in the root directory of the repository.

## Usage

### Configuration file

The application uses a configuration file to specify the
Kafka broker and the topic to use, as well as the optional
Fernet symmetric key to use for encrypting the data. The configuration file
is a JSON with this structure:

```json
{
  "kafkaconf" : {
    "bootstrap.servers": "abc.swedencentral.azure.confluent.cloud:9092",
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": "TRNHSNRJS5342HSKF",
    "sasl.password": "DwQpxSDPnjvtc54mv6C4TBzmLfcfyA8EzAYgMjfRQTvmcUCZ7thnCpGV4jE622vd"
  },
  "topic": "chat",
  "symmetric_key": "9gWFwrEng_gmYTz1uN_PlnlGs4te0MqIOObQFcsns3E="
}
```

### Running the application

Start the application by typing

```powershell
chatwithkafka /path/to/config.json
```

You can also see options by typing

```powershell
chatwithkafka --help
usage: chatwithkafka.exe [-h] [-u USER] [-t TOPIC] [--key KEY] config_file

Chat Terminal User Interface (TUI) with Kafka

positional arguments:
config_file              Path to the JSON configuration file

options:
-h, --help               Show this help message and exit
-u USER, --user USER     User name to use in chat. If none is provided, the currently logged in user's name will be used
-t TOPIC, --topic TOPIC  Topic to use for chat. Overrides the topic in the configuration file
--key KEY                Symmetric Fernet key to use encrypting and decrypting messages. Overrides the key in the configuration file
```

### Exiting the application

Press `Esc` to exit the chat application.

### Secured Communication

Using the [`cryptography`](https://cryptography.io/en/latest/) library, the application can 
encrypt the message it sends as well as decrypt the messages it receives. The symmetric key
used for encryption and decryption is specified in the configuration file or 
sent in as a command line argument (`--key`). If no key is provided, then the messages
are sent in plain text.

There is a key generation tool also installed with the application. To generate a key, type

```powershell
chatwithkafka-keygen
```

and it will provide a key (e.g. `h1-lkBmvVizjEKpEAmirtvaWUmrwhNhe0xtgCeGe5FU=`) that can be shared with the other users of the chat,
in some other way of communicating than the chat itself.

**Note that the encryption here is symmetric for simlicity's sake, so all users
who want to communicate needs to have the same key as input to the program.**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
