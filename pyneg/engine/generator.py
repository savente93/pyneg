from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from typing import Set


class Generator:
    '''
    Generator empty class that is used soley for type annotations

    :raises NotImplementedError
    :raises NotImplementedError
    '''

    def __init__(self):
        raise NotImplementedError()

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        raise NotImplementedError()

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        raise NotImplementedError()
