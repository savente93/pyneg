"""
Generator Nothing but an abstract class. Sometimes used for type annotations
and as a template for implementing your own. Generators are what
agent engines use to generate offers. All logic relating to reasoning
and finding potential offers should be located here.
"""

from typing import Optional, Set

from pyneg.comms import AtomicConstraint, Offer
from pyneg.types import AtomicDict


class Generator:
    """
    Nothing but an abstract class. Sometimes used for type annotations
    and as a template for implementing your own. Generators are what
    agent engines use to generate offers. All logic relating to reasoning
    and finding potential offers should be located here.

    - utilities: a utility mapping.
    - knowledge_base: a knowledge base. only supported if the generator uses ProbLog
    - acceptability_threshold: minimum utility needed for the agent to accept an offer

    """


    def __init__(self):
        self.utilities = {}
        self.knowledge_base = []
        self.neg_space = {}
        self.acceptability_threshold = 0.0
        self.active = False

    def generate_offer(self) -> Offer:
        """
        Generates the next offer the agent should propose.

        :raises NotImplementedError:
        :return: The offer the agent should propose
        :rtype: Offer
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

    def get_constraints(self) -> Set[AtomicConstraint]:
        """
        Returns a set containing all the constraints known.

        :raises NotImplementedError: [description]
        :return: A set of all known constraints.
        :rtype: Set[AtomicConstraint]
        """
        raise NotImplementedError()

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        """
        Returns the constraint that is violating the given offer if any.

        :param offer: The offer to check
        :type offer: Offer
        :raises NotImplementedError: [description]
        :return: The constraint that is being violated by the offer if any.
        :rtype: Optional[AtomicConstraint]
        """
        raise NotImplementedError()

    def get_unconstrained_values_by_issue(self, issue: str) -> Set[str]:
        """
        Return a set of all values associated with an issue that are not ruled out by
        any constraint.

        :param issue: The issue to get the values for.
        :type issue: str
        :raises NotImplementedError:
        :return: A set of all unconstrained values. Could be empty.
        :rtype: Set[str]
        """
        raise NotImplementedError()
