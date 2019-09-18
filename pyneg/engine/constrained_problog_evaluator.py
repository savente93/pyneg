from typing import Optional, List, Set, Iterable

from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict, NegSpace
from pyneg.utils import atom_from_issue_value
from .problog_evaluator import ProblogEvaluator
from .strategy import Strategy


class ConstrainedProblogEvaluator(ProblogEvaluator):
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 kb: List[str],
                 constr_value: float,
                 initial_constraints: Optional[Set[AtomicConstraint]]):
        self.constr_value = constr_value
        super().__init__(neg_space, utilities, non_agreement_cost, kb)
        self.constraints: Set[AtomicConstraint] = set()
        if initial_constraints:
            self.constraints.update(initial_constraints)

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

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        self.constraints.add(constraint)
        constraint_atom = atom_from_issue_value(constraint.issue, constraint.value)
        self._add_utilities({constraint_atom: self.constr_value})
        for issue in self.neg_space.keys():
            if len(self.get_unconstrained_values_by_issue(issue)) <= 0:
                self.constraints_satisfiable = False
                return False

        return True

    def add_constraints(self, constraints: Iterable[AtomicConstraint]) -> bool:
        self.constraints.update(constraints)
        self._add_utilities({atom_from_issue_value(constraint.issue, constraint.value) : self.constr_value
                             for constraint in self.constraints})
        for issue in self.neg_space.keys():
            if len(self.get_unconstrained_values_by_issue(issue)) <= 0:
                self.constraints_satisfiable = False
                return False

        return True

    def _add_utilities(self, new_utils):
        self.utilities = {
            **self.utilities,
            **new_utils
        }

    def get_unconstrained_values_by_issue(self, issue):
        issue_constrained_values = set(
            constr.value for constr in self.constraints if constr.issue == issue)
        issue_unconstrained_values = set(
            self.neg_space[issue]) - issue_constrained_values
        return issue_unconstrained_values

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils

        return self.constraints_satisfiable

    def calc_assignment_util(self, issue: str, value: str) -> float:
        for constr in self.constraints:
            if not constr.is_satisfied_by_assignment(issue, value):
                return self.non_agreement_cost

        return super().calc_assignment_util(issue, value)
