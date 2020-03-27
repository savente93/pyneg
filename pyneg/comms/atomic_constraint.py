"""
This module defines an atomic constraint, the simples form of constraint possible.
It expresses that any offer which has a perticular assignement will never be accepted.
Good baseline for addapting for more complicated constraints
"""

from numpy import isclose

from .offer import Offer



class AtomicConstraint():
    """
        Atomic constraint, the simples form of constraint possible.
        It expresses that any offer which has a perticular assignement will never be accepted.
        Good baseline for addapting for more complicated constraints
    """
    def __init__(self, issue: str, value: str):
        self.issue = str(issue)
        self.value = str(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtomicConstraint):
            return False

        if self.issue != other.issue:
            return False

        if self.value != other.value:
            return False

        return True

    def is_satisfied_by_assignment(self, issue: str, value: str) -> bool:
        """
        Determines whether a perticular assignement satisfies this constraint.
        For example:
        >>> AtomicConstraint("A","first").is_satisfied_by_assignment("A","first")
        False
        >>> AtomicConstraint("A","first").is_satisfied_by_assignment("A","second")
        True

        :param issue: The issue the potential assignement is refering too
        :type issue: str
        :param value: The value the potential assignement is refering too
        :type value: str
        :return: True iff the assignement is satisfied
        :rtype: bool
        """
        return not (issue == self.issue and value == self.value)

    def is_satisfied_by_offer(self, offer: Offer) -> bool:
        """
        Checks if a whole offer is satisfied by the constraint.
        For atomic constraints this means just checking all of the
        assignements individually.

        :param offer: The offer to be checked
        :type offer: Offer
        :return: True iff the assignement is allowed under this constraint
        :rtype: bool
        """
        chosen_value = offer.get_chosen_value(self.issue)
        if chosen_value == self.value:
            return False

        return True

    # string type is to avoid circular dependencies wiht AtomicConstraint
    def is_satisfied_by_strat(self, strat: 'Strategy') -> bool:# type: ignore
        """
        Checks if a whole Stratagy is satisfied by the constraint.
        i.e. does the stratagy assign 0 probability to the constrained assignement?

        :param strat: The strattagy to be checked
        :type strat: Stratagy
        :return: True iff the assignement is allowed under this constraint
        :rtype: bool
        """
        return isclose(strat.get_value_dist(self.issue)[self.issue], 0)

    def __hash__(self) -> int:
        return hash((self.issue, self.value))

    def __repr__(self) -> str:
        return "{issue}!={value}".format(issue=self.issue, value=self.value)
