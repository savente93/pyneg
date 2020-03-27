"""
Nothing but an abstract class. Sometimes used for type annotations
and as a template for implementing your own. Evaluators are what
agent engines use to evaluate offers. All logic relating to reasoning
and evaluating potential offers should be located here.
"""

from typing import Set

from pyneg.comms import AtomicConstraint, Offer
from pyneg.types import AtomicDict


class Evaluator():
    """
    Nothing but an abstract class. Sometimes used for type annotations
    and as a template for implementing your own. Evaluators are what
    agent engines use to evaluate offers. All logic relating to reasoning
    and evaluating potential offers should be located here.
    """
    def __init__(self):
        pass

    def calc_offer_utility(self, offer: Offer) -> float:
        """
        Calculates the utility of an offer in whatever way is appropriate.

        :param offer: the offer you want to know the utility of
        :type offer: Offer
        :raises NotImplementedError: self-explanatory
        :return: The utility of the offer
        :rtype: float
        """
        raise NotImplementedError()

    def calc_assignment_util(self, issue: str, value: str) -> float:
        """
        Calculates the utility of a single issue value assignement.
        Only possible for linear additive utility functions.

        :param issue: the issue the assignements is refering too
        :type issue: str
        :param value: the potential value of the assignement
        :type value: str
        :raises NotImplementedError:
        :return: The increase in utility that the assignement would cause
        :rtype: float
        """
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        """
        Add utilities to the knowledge base. Returns true if there are
        still potential acceptable solutions. If the evaluator doesn't reason
        about this, it should always return true.


        :param new_utils: an atomic dictionary of the utilities to add
        :type new_utils: AtomicDict
        :raises NotImplementedError:
        :return: should return true if there are still potentially offers \
        possible.
        :rtype: bool
        """
        raise NotImplementedError()

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        """
        sets the utilities in the knowledge base. Returns true if there are
        still potential acceptable solutions. If the evaluator doesn't reason
        about this, it should always return true. similar to add-utilities but
        overwrites all previous utilities.


        :param new_utils: an atomic dictionary of the utilities to add
        :type new_utils: AtomicDict
        :raises NotImplementedError:
        :return: should return true if there are still potentially offers \
        possible.
        :rtype: bool
        """
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        """
        Add the given constraint to the knowledge base. Returns true if there are
        still potential acceptable solutions. If the agent doesn't reason about
        constrints, this should be a no-op and always return true.

        :param constraint: The constraint to add
        :type constraint: AtomicConstraint
        :raises NotImplementedError:
        :return: Whether there are still potential acceptable solutions
        :rtype: bool
        """
        raise NotImplementedError()

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        """
        Add multiple constraints to the knowledge base. Returns true if there are
        still potential acceptable solutions. If the agent doesn't reason about
        constrints, this should be a no-op and always return true.

        :param constraint: The constraint to add
        :type constraint: AtomicConstraint
        :raises NotImplementedError:
        :return: Whether there are still potential acceptable solutions
        :rtype: bool
        """
        raise NotImplementedError()
