from enum import Enum, auto


class MessageType(Enum):
    empty = auto(),
    terminate = auto(),
    offer = auto(),
    accept = auto()
