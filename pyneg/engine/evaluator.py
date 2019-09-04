from pyneg.comms import Offer
from pyneg.types import AtomicDict


class Evaluator():
    def __init__(self):
        raise NotImplementedError()

    def calc_offer_utility(self, offer: Offer) -> float:
        raise NotImplementedError()

    def calc_assignment_util(self, issue: str, value: str) -> float:
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> None:
        raise NotImplementedError()
