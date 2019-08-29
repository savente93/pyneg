from enum import IntEnum
from typing import Dict, Tuple, List, Optional, cast


class Verbosity(IntEnum):
    none = 0
    messages = 1
    reasoning = 2
    debug = 3
