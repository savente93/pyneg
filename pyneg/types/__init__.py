'''
This module defines constants and types used elsewhere.
The Types are for type annotations only.
Examples:
>>> neg_space = {"First":["A","B"], "Second":["C","D"]}
>>> nested = {"First": {"A":0, "B":1}, "Second":{"C":1,"D":0}}
>>> atomic = {"First_A":0, "First_B":1, "Second_C":1, "Second_D":0}
'''

from typing import Dict, Tuple, Union, cast, List, Optional
from pyneg.types.message_type import MessageType
from pyneg.types.verbosity import Verbosity

AtomicDict = Dict[str, float]
NestedDict = Dict[str, Dict[str, float]]
NegSpace = Dict[str, List[str]]
