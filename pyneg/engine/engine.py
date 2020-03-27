"""
This module defines the AbstractEngine and Engine classes.
AbstractEngine is just a template used for type annotations.
Engine is just a wrapper/addaptor for an Evaluator and Generator.
"""

from typing import Optional, Set

from pyneg.comms import AtomicConstraint, Offer
from pyneg.engine.evaluator import Evaluator
from pyneg.engine.generator import Generator
from pyneg.types import AtomicDict


class AbstractEngine:
    """
    AbstractEngine class is mostly used for type annotations and provides
    a template for implementing new engines.
    """
    def __init__(self):
        pass

    def generate_offer(self) -> Offer:
        """
        Generates the next offer the agent should propose.

        :raises NotImplementedError:
        :return: The offer the agent should propose
        :rtype: Offer
        """
        raise NotImplementedError()

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

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        """
        Add utilities to the knowledge base. Returns true if there are \
        still potential acceptable solutions. If the evaluator doesn't reason \
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

    def get_unconstrained_values_by_issue(self, issue):
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

    def get_constraints(self) -> Set[AtomicConstraint]:
        """
        Returns a set containing all the constraints known.

        :raises NotImplementedError: [description]
        :return: A set of all known constraints.
        :rtype: Set[AtomicConstraint]
        """
        raise NotImplementedError()

    def accepts(self, offer: Offer) -> bool:
        """
        Determines whether the agent finds an offer acceptable.
        Usually this is decided by determining whether the utility
        of the offer is higher than the reservation value.

        :param offer: The offer to consider
        :type offer: Offer
        :raises NotImplementedError: [description]
        :return: True if the offer is acceptable according to the \
        known criteria.
        :rtype: bool
        """
        raise NotImplementedError()

    def can_continue(self) -> bool:
        """
        Determines whether the engine can generate new proposals.

        :raises NotImplementedError: [description]
        :return: True if the engine can generate new proposals.
        :rtype: bool
        """
        raise NotImplementedError()

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        """
        Determines whether an offer satisfies all known constraints.

        :param offer: The offer to check
        :type offer: Offer
        :raises NotImplementedError:
        :return: True if the offer is allowed under the constraints.
        :rtype: bool
        """
        raise NotImplementedError()


class Engine(AbstractEngine):
    """
    This class is where all of the reasoning about offers
    happens. Mostly it's a wrapper for the Generator and Evaluator class
    """
    def __init__(self, generator: Generator, evaluator: Evaluator):
        super().__init__()
        self.generator: Generator = generator
        self.evaluator: Evaluator = evaluator
        self._accepts_all = False

    def generate_offer(self) -> Offer:
        """
        Generates the next offer the agent should propose.

        :return: The offer the agent should propose
        :rtype: Offer
        """
        return self.generator.generate_offer()

    def calc_offer_utility(self, offer: Offer) -> float:
        """
        Calculates the utility of an offer in whatever way is appropriate.

        :param offer: the offer you want to know the utility of
        :type offer: Offer
        :return: The utility of the offer
        :rtype: float
        """
        return self.evaluator.calc_offer_utility(offer)

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        """
        Add utilities to the knowledge base. Returns true if there are
        still potential acceptable solutions. If the evaluator doesn't reason
        about this, it should always return true.


        :param new_utils: an atomic dictionary of the utilities to add
        :type new_utils: AtomicDict
        :return: should return true if there are still potentially offers \
        possible.
        :rtype: bool
        """
        self.evaluator.add_utilities(new_utils)
        return self.generator.add_utilities(new_utils)

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        """
        sets the utilities in the knowledge base. Returns true if there are
        still potential acceptable solutions. If the evaluator doesn't reason
        about this, it should always return true. similar to add-utilities but
        overwrites all previous utilities.


        :param new_utils: an atomic dictionary of the utilities to add
        :type new_utils: AtomicDict
        :return: should return true if there are still potentially offers \
        possible.
        :rtype: bool
        """
        self.evaluator.add_utilities(new_utils)
        return self.generator.add_utilities(new_utils)

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        """
        Add the given constraint to the knowledge base. Returns true if there are
        still potential acceptable solutions. If the agent doesn't reason about
        constrints, this should be a no-op and always return true.

        :param constraint: The constraint to add
        :type constraint: AtomicConstraint
        :return: Whether there are still potential acceptable solutions
        :rtype: bool
        """
        return self.generator.add_constraint(constraint)

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        """
        Add multiple constraints to the knowledge base. Returns true if there are
        still potential acceptable solutions. If the agent doesn't reason about
        constrints, this should be a no-op and always return true.

        :param constraint: The constraint to add
        :type constraint: AtomicConstraint
        :return: Whether there are still potential acceptable solutions
        :rtype: bool
        """
        return self.generator.add_constraints(new_constraints)

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        """
        Returns the constraint that is violating the given offer if any.

        :param offer: The offer to check
        :type offer: Offer
        :return: The constraint that is being violated by the offer if any.
        :rtype: Optional[AtomicConstraint]
        """
        return self.generator.find_violated_constraint(offer)

    def get_unconstrained_values_by_issue(self, issue: str) -> Set[str]:
        """
        Return a set of all values associated with an issue that are not ruled out by
        any constraint.

        :param issue: The issue to get the values for.
        :type issue: str
        :return: A set of all unconstrained values. Could be empty.
        :rtype: Set[str]
        """
        return self.generator.get_unconstrained_values_by_issue(issue)

    def get_constraints(self) -> Set[AtomicConstraint]:
        """
        Returns a set containing all the constraints known.

        :return: A set of all known constraints.
        :rtype: Set[AtomicConstraint]
        """
        return self.generator.get_constraints()

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        """
        Determines whether an offer satisfies all known constraints.

        :param offer: The offer to check
        :type offer: Offer
        :return: True if the offer is allowed under the constraints.
        :rtype: bool
        """
        for constr in self.generator.get_constraints():
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True

    def accepts(self, offer: Offer) -> bool:
        """
        Determines whether the agent finds an offer acceptable.
        Usually this is decided by determining whether the utility
        of the offer is higher than the reservation value.

        :param offer: The offer to consider
        :type offer: Offer
        :return: True if the offer is acceptable according to the \
        known criteria.
        :rtype: bool
        """
        if self._accepts_all:
            return True

        return self.evaluator.calc_offer_utility(offer) >= self.generator.acceptability_threshold

    def can_continue(self) -> bool:
        """
        Determines whether the engine can generate new proposals.

        :return: True if the engine can generate new proposals.
        :rtype: bool
        """
        return self.generator.active
