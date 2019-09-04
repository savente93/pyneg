from pyneg.comms import Offer
from pyneg.types import AtomicDict
from .evaluator import Evaluator
from .generator import Generator


class Engine():
    def __init__(self, generator: Generator, evaluator: Evaluator):
        self.generator: Generator = generator
        self.evaluator: Evaluator = evaluator

    def generate_offer(self) -> Offer:
        return self.generator.generate_offer()

    def calc_offer_utility(self, offer: Offer) -> float:
        return self.evaluator.calc_offer_utility(offer)

    def add_utilities(self, new_utils: AtomicDict) -> None:
        self.generator.add_utilities(new_utils)
        self.evaluator.add_utilities(new_utils)

    def set_utilities(self, new_utils: AtomicDict) -> None:
        self.generator.add_utilities(new_utils)
        self.evaluator.add_utilities(new_utils)


class AbstractEngine(Engine):
    def __init__(self):
        pass

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def calc_offer_utility(self, offer: Offer) -> float:
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> None:
        raise NotImplementedError()

    def set_utilities(self, new_utils: AtomicDict) -> None:
        raise NotImplementedError()
