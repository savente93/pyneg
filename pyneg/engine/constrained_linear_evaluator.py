"""
Defines the :class:`ConstrainedLinearEvaluator` class, the contraint aware version of
:class:`LinearEvaluator`
"""

from typing import Dict, Set, Union

from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from pyneg.engine.linear_evaluator import LinearEvaluator, Strategy


class ConstrainedLinearEvaluator(LinearEvaluator):
    """
    This class is the contraint aware version of :class:`LinearEvaluator`. It works the
    same except that for any offer that violates one of the known constraints
    it returns a utility of constr_value.
    """
    def __init__(self, utilities: AtomicDict,
                 issue_weights: Dict[str, float],
                 non_agreement_cost: float,
                 constr_value: float,
                 initial_constraints: Set[AtomicConstraint]):
        self.constr_value = constr_value
        super().__init__(utilities, issue_weights, non_agreement_cost)
        self.constraints: Set[AtomicConstraint] = set()
        if initial_constraints:
            self.constraints.update(initial_constraints)



    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        self.constraints.add(constraint)
        return True

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        self.constraints.update(new_constraints)
        return True

    def calc_assignment_util(self, issue: str, value: str) -> float:
        if not all([constr.is_satisfied_by_assignment(issue, value)
                    for constr in self.constraints]):
            return self.constr_value

        return super().calc_assignment_util(issue, value)

    def calc_offer_utility(self, offer: Offer) -> float:
        if not self.satisfies_all_constraints(offer):
            return self.constr_value

        return super().calc_offer_utility(offer)

    def calc_strat_utility(self, strat: Strategy) -> float:
        if not self.satisfies_all_constraints(strat):
            return self.constr_value

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
