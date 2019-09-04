from typing import Optional, List, Set, Iterable

from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from pyneg.types import NegSpace
from .problog_evaluator import ProblogEvaluator
from .strategy import Strategy


class ConstrainedProblogEvaluator(ProblogEvaluator):
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 kb: List[str],
                 initial_constraints: Optional[Set[AtomicConstraint]]):

        super().__init__(neg_space, utilities, non_agreement_cost, kb)
        self.constraints = set()
        if initial_constraints:
            self.constraints.add(initial_constraints)

    def calc_offer_utility(self, offer: Offer) -> float:
        if not self.satisfies_all_constraints(offer):
            return self.non_agreement_cost
        else:
            return super().calc_offer_utility(offer)

    def calc_strat_utility(self, strat: Strategy) -> float:
        if not self.satisfies_all_constraints(strat):
            return self.non_agreement_cost
        else:
            return super().calc_strat_utility(strat)

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)

    def add_constraints(self, constraints: Iterable[AtomicConstraint]) -> None:
        self.constraints.update(constraints)

    def calc_assignment_util(self, issue: str, value: str) -> float:
        for constr in self.constraints:
            if not constr.is_satisfied_by_assignment(issue, value):
                return self.non_agreement_cost

        return super().calc_assignment_util(issue, value)
