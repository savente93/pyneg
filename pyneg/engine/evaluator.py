from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from typing import Set


class Evaluator():
    def __init__(self):
        raise NotImplementedError()

    def calc_offer_utility(self, offer: Offer) -> float:
        raise NotImplementedError()

    def calc_assignment_util(self, issue: str, value: str) -> float:
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        raise NotImplementedError()

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        raise NotImplementedError()

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        raise NotImplementedError()
