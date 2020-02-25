"""
A message type definitnion for easier checking and type annotations.
"""
from enum import Enum, auto


class MessageType(Enum):
    """
    EMPTY: No message, just a stub
    EXIT: sender is exiting the negotiation without agreement
    OFFER: A proposal with optionally a constraint
    ACCEPT: Agent has accepted the offer in this message
    """
    EMPTY = auto()
    EXIT = auto()
    OFFER = auto()
    ACCEPT = auto()
