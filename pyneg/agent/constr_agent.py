"""
This module contains the logic for agents that know how to reason about constraints.
It basically only contains the ConstrainedAgent class
"""

from typing import Set

from pyneg.comms import AtomicConstraint, Offer
from pyneg.types import NegSpace

from . import Agent


class ConstrainedAgent(Agent):
    """
    A negotiation agent that has additional logic to deal with constraints.
    For now only atomic constraints are supported

    Public functions:
        - add_constraint(self, constraint) -> None
        - get_unconstrainted_values_by_issue(self,issue) -> Set[str]
        - get_constraints(self) -> Set[AtomicConstraint]
        - accepts(self, offer: Offer) -> bool

    """
    def __init__(self):
        """
        constraint agent constructor. As with other agents, everything is set by the factory
        """
        super().__init__()
        self._constraints_satisfiable = True

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        """
        Register a constraint with the agent and it's engine
        :param constraint: the constraint to be added
        :type constraint: AtomicConstraint
        """
        self._engine.add_constraint(constraint)

    def get_unconstrained_values_by_issue(self, issue) -> Set[str]:
        """
        Returns a set containing all unconstrained values for a specific issue

        :param issue: The issue of which to retreive the unconstrained values
        :type issue: bool
        :return: A set containing all value strings that have no known\
        constraint associated
        :rtype: Set[str]
        """
        return self._engine.get_unconstrained_values_by_issue(issue)

    def get_constraints(self) -> Set[AtomicConstraint]:
        """
        Returns a set containing all the constraints known to this agent

        :return: Set containing all the constraints known to this agent
        :rtype: Set[AtomicConstraint]
        """
        return self._engine.get_constraints()

    def _accepts_negotiation_proposal(self, neg_space: NegSpace) -> bool:
        """
        Decide whether we should accept the proposal for a negotiation.\
        We accept whenever the negotiatin space being proposed is equal to our own\
        so we can reason about it, and there are still solutions possible.

        :param neg_space: The negotiation space the proposed negotiation will take part in
        :type neg_space: NegSpace
        :return: Whether the agents agrees to start a negotiation
        :rtype: bool
        """
        return self._neg_space == neg_space and self._constraints_satisfiable

    def accepts(self, offer: Offer) -> bool:
        """
        Determines whether the agent finds the provided offer acceptable.

        :param offer: The offer to consider
        :type offer: Offer
        :return: True if and only if the agent accepts the proposal
        :rtype: bool
        """
        if not self._engine.satisfies_all_constraints(offer):
            return False

        return super().accepts(offer)
