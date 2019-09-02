from typing import Optional, Set, Dict, List
from pyneg.comms import Offer
from pyneg.types import NegSpace, NestedDict, AtomicDict
from .evaluators import Evaluator
from .strategy import Strategy
from numpy.random import choice
from .generators import EnumGenerator, DTPGenerator, RandomGenerator
from pyneg.comms import AtomicConstraint


class ConstrainedEnumGenerator(EnumGenerator):
    def __init__(self, neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 acceptability_prec: float,
                 initial_constraints: Optional[Set[AtomicConstraint]],
                 auto_constraints=True) -> None:
        super().__init__(neg_space, utilities, evaluator, acceptability_prec)
        self.constraints = set()
        if initial_constraints:
            self.constraints.add(initial_constraints)
        self.auto_constraints = auto_constraints

    def init_generator(self) -> None:
        raise NotImplementedError()

    def generate_fisrt_offer(self) -> Offer:
        raise NotImplementedError()

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def offer_from_index_dict(self, index_dict: Dict[str, int]) -> Offer:
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)

    def add_constraints(self, constraints: List[AtomicConstraint]) -> None:
        self.constraints.update(constraints)

    def generate_constraints(self, offer: Offer) -> Offer:
        raise NotImplementedError()

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True


class ConstrainedRandomGenerator(RandomGenerator):
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 non_agreement_cost: float,
                 kb: List[str],
                 acceptability_prec: float,
                 initial_constraints: Optional[Set[AtomicConstraint]],
                 auto_constraints=True,
                 max_generation_tries: int = 500):
        self.constraints = set()
        if initial_constraints:
            self.constraints.add(initial_constraints)
        self.auto_constraints = auto_constraints
        raise NotImplementedError()

    def init_uniform_strategy(self, neg_space: NegSpace) -> None:
        raise NotImplementedError()

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)

    def add_constraints(self, constraints: List[AtomicConstraint]) -> None:
        self.constraints.update(constraints)

    def generate_constraints(self, offer: Offer) -> Offer:
        raise NotImplementedError()

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True


class ConstrainedDTPGenerator(DTPGenerator):

    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 acceptability_prec: float,
                 kb: List[str],
                 initial_constraints: Optional[Set[AtomicConstraint]],
                 auto_constraints=True):
        self.constraints = set()
        if initial_constraints:
            self.constraints.add(initial_constraints)
        self.auto_constraints = auto_constraints
        raise NotImplementedError()

    def reset_generator(self):
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> None:
        raise NotImplementedError()

    def compile_dtproblog_model(self):
        raise NotImplementedError()

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)

    def add_constraints(self, constraints: List[AtomicConstraint]) -> None:
        self.constraints.update(constraints)

    def generate_constraints(self, offer: Offer) -> Offer:
        raise NotImplementedError()

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True
