from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from typing import Set, Optional


class Generator:
    '''
    Generator empty class that is used soley for type annotations

    :raises NotImplementedError
    :raises NotImplementedError
    '''

    def __init__(self):
        self.utilities = {}
        self.kb = []
        self.neg_space = {}
        self.acceptability_threshold = 0.0

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

    def get_constraints(self):
        raise NotImplementedError()

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        raise NotImplementedError()

    def get_unconstrained_values_by_issue(self, issue: str) -> Set[str]:
        raise NotImplementedError()
