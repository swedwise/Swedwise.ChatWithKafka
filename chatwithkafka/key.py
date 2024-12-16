from argparse import ArgumentParser

from cryptography.fernet import Fernet


def key_cli():
    """Command line interface for generating a Fernet key"""
    parser = ArgumentParser(
        description="Key generation for the chat with Kafka app",
        epilog="Use this to produce a key which you share with all chat participants you want to share encypted communication with."
    )
    _ = parser.parse_args()

    key = Fernet.generate_key()
    print(key.decode())



if __name__ == '__main__':
    key_cli()