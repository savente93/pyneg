from typing import Optional, Set, Dict, List
from pyneg.comms import Offer
from pyneg.types import NegSpace, NestedDict, AtomicDict
from .evaluator import Evaluator
from .strategy import Strategy
from numpy.random import choice
from pyneg.comms import AtomicConstraint
from .generator import Generator
from .dtp_generator import DTPGenerator


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

    def reset_generator(self):
        super().reset_generator()
        self.constraints = set()

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)

    def add_constraints(self, constraints: List[AtomicConstraint]) -> None:
        self.constraints.update(constraints)

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True

    def add_utilities(self, new_utils):
        super().add_utilities(new_utils)

        if self.auto_constraints:
            self.add_constraints(self.generate_new_constraints())

    def compile_dtproblog_model(self):
        raise NotImplementedError()

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def generate_constraints(self, offer: Offer) -> Offer:
        raise NotImplementedError()
