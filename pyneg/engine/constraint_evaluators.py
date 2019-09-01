from pyneg.comms import Offer, AtomicConstraint
from typing import Dict, Union, Optional, List, Set
from pyneg.utils import atom_from_issue_value
from pyneg.types import AtomicDict
from .strategy import Strategy
from .evaluators import LinearEvaluator, ProblogEvaluator
from pyneg.types import NegSpace
from problog.program import PrologString
from problog import get_evaluatable
from problog.tasks.dtproblog import dtproblog


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

    def calc_offer_utility(self, offer: Offer) -> float:
        if not self.satisfies_all_constraints(offer):
            return self.non_agreement_cost
        else:
            super().calc_offer_utility(offer)

    def calc_strat_utility(self, strat: Strategy) -> float:
        if not self.satisfies_all_constraints(strat):
            return self.non_agreement_cost
        else:
            super().calc_strat_utility(strat)

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_strat(offer):
                return False

        return True


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
            super().calc_offer_utility(offer)

    def calc_strat_utility(self, strat: Strategy) -> float:
        if not self.satisfies_all_constraints(strat):
            return self.non_agreement_cost
        else:
            super().calc_strat_utility(strat)

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_strat(offer):
                return False

        return True

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)
