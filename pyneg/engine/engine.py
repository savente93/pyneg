from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from pyneg.engine.evaluator import Evaluator
from pyneg.engine.generator import Generator
from typing import Set, Optional


class Engine:
    def __init__(self, generator: Generator, evaluator: Evaluator):
        self.generator: Generator = generator
        self.evaluator: Evaluator = evaluator

    def generate_offer(self) -> Offer:
        return self.generator.generate_offer()

    def calc_offer_utility(self, offer: Offer) -> float:
        return self.evaluator.calc_offer_utility(offer)

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        self.evaluator.add_utilities(new_utils)
        return self.generator.add_utilities(new_utils)

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.evaluator.add_utilities(new_utils)
        return self.generator.add_utilities(new_utils)

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        return self.generator.add_constraint(constraint)

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        return self.generator.add_constraints(new_constraints)

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        return None


class AbstractEngine(Engine):
    def __init__(self):
        pass

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def calc_offer_utility(self, offer: Offer) -> float:
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        raise NotImplementedError()

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        raise NotImplementedError()

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        raise NotImplementedError()
