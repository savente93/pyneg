from typing import Dict, Optional, Set

from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from .linear_evaluator import LinearEvaluator
from .strategy import Strategy


class ConstrainedLinearEvaluator(LinearEvaluator):
    def __init__(self, utilities: AtomicDict,
                 issue_weights: Dict[str, float],
                 non_agreement_cost: float,
                 initial_constraints: Optional[Set[AtomicConstraint]]):

        super().__init__(utilities, issue_weights, non_agreement_cost)
        self.constraints = set()
        if initial_constraints:
            self.constraints.add(initial_constraints)

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)

    def add_constraints(self, constraints: AtomicConstraint) -> None:
        self.constraints.update(constraints)

    def calc_assignment_util(self, issue: str, value: str) -> float:
        if not all([constr.is_satisfied_by_assignment(issue, value) for constr in self.constraints]):
            return self.non_agreement_cost
        else:
            return super().calc_assignment_util(issue, value)

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
