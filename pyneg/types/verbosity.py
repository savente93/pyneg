"""
Enum type for more understandable verbosity levels.
hopefully quite self-describing.
"""

from enum import IntEnum


class Verbosity(IntEnum):
    """
    None: No output.
    Messages: print each message as it is sent to another agent
    reasoning: Additionally print reasoning that led to the message
    debug: print absolutely everything.
    """
    none = 0
    messages = 1
    reasoning = 2
    debug = 3
