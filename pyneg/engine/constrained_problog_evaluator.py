"""
Defines the :class:`ConstrainedProblogEvaluator` class, the contraint aware version of
:class:`ProblogEvaluator` see that entry for more information.
"""
from typing import Optional, List, Set, Iterable, Union

from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict, NegSpace
from pyneg.utils import atom_from_issue_value
from .problog_evaluator import ProblogEvaluator
from .strategy import Strategy


class ConstrainedProblogEvaluator(ProblogEvaluator):
    """
        This class is equal to the :class:`ProblogEvaluator` class but with
        additional logic to handle constraints. See :class:`ProblogEvaluator` for
        more information on how ProbLog is used.
    """
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 knowledge_base: List[str],
                 constr_value: float,
                 initial_constraints: Optional[Set[AtomicConstraint]]):
        self.constr_value = constr_value
        super().__init__(neg_space, utilities, non_agreement_cost, knowledge_base)
        self.constraints: Set[AtomicConstraint] = set()
        self.constraints_satisfiable = True
        if initial_constraints:
            self.constraints.update(initial_constraints)

    def calc_offer_utility(self, offer: Offer) -> float:
        if not self.satisfies_all_constraints(offer):
            return self.non_agreement_cost

        return super().calc_offer_utility(offer)

    def calc_strat_utility(self, strat: Strategy) -> float:
        if not self.satisfies_all_constraints(strat):
            return self.non_agreement_cost

        return super().calc_strat_utility(strat)

    def satisfies_all_constraints(self, to_check: Union[Offer, Strategy]) -> bool:
        """
        Checks whether the given offer or strategy  satisfies all known constraints.

        :param to_check: The offer or strategy to check
        :type to_check: Union[Offer, Strategy]
        :raises TypeError: if an object of unknown type is passed.
        :return: True iff the given offer or strategy satisfies all known constraints.
        :rtype: bool
        """
        if isinstance(to_check, Offer):
            for constr in self.constraints:
                if not constr.is_satisfied_by_offer(to_check):
                    return False
        elif isinstance(to_check, Strategy):
            for constr in self.constraints:
                if not constr.is_satisfied_by_strat(to_check):
                    return False
        else:
            raise TypeError(f"""object is of type {type(to_check)} instead of
                                Union[Offer, Strategy]. Object: {to_check}""")

        return True

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        self.constraints.add(constraint)
        constraint_atom = atom_from_issue_value(constraint.issue, constraint.value)
        self._add_utilities({constraint_atom: self.constr_value})
        for issue in self.neg_space.keys():
            if not self.get_unconstrained_values_by_issue(issue):
                self.constraints_satisfiable = False
                return False

        return True

    def add_constraints(self, new_constraints: Iterable[AtomicConstraint]) -> bool:
        self.constraints.update(new_constraints)
        self._add_utilities({atom_from_issue_value(constraint.issue, constraint.value):
                             self.constr_value
                             for constraint in self.constraints})
        for issue in self.neg_space.keys():
            if not self.get_unconstrained_values_by_issue(issue):
                self.constraints_satisfiable = False
                return False

        return True

    def _add_utilities(self, new_utils):
        self.utilities = {
            **self.utilities,
            **new_utils
        }

    def get_unconstrained_values_by_issue(self, issue: str) -> Set[str]:
        """
        This function returns all known values for the given issue that are not \
        ruled out by a constraint.

        :param issue: The issue to retreive the unconstrained values of.
        :type issue: str
        :return: A set containt all values of an issue that are not constrained
        :rtype: Set[AtomicConstraint]
        """
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
