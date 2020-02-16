from enum import Enum, auto


class MessageType(Enum):
    EMPTY = auto()
    EXIT = auto()
    OFFER = auto()
    ACCEPT = auto()
