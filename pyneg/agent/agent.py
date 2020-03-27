""" This module defines the base agent class. Here is where a lot of the
communication logic and the main negotiation loop is defined.
"""

from typing import Dict, List, Optional

from pyneg.comms import AtomicConstraint, Message, Offer
from pyneg.engine import AbstractEngine
from pyneg.types import MessageType, NegSpace


class Agent:
    """
     Base negotiation agent. This class handles most things like the main
     negotiation loop, communication, and genrally acts like a hub
     for other classes.

     Public Methods:
       - receive_negotiation_request(self, opponent: Agent, neg_space: NegSpace) -> bool:
       - negotiate(self, opponent: Agent) -> bool:
       - send_message(self, opponent: Agent, msg: Message) -> None
       - receive_message(self, msg: Message) -> None
       - generate_next_message(self) -> Message
       - add_utilities(self, new_utils: Dict[str, float]) -> bool
       - set_utilities(self, new_utils: Dict[str, float]) -> bool
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        """Setup all the class attributes, but we don't assign them meaningful
            values here. That is all handled by the factory. They are initialised here
            to make the linters a bit happier.
        """
        self.name: str = "" #: Name of the agent. mainly used for logging
        self._transcript: List[Message] = []
        self._max_rounds: int = 0
        self._neg_space: NegSpace = {}
        self._engine: AbstractEngine = AbstractEngine()
        self._absolute_reservation_value: float = -(2.0 ** 31)
        self.opponent: Optional[Agent] = None
        self._type = ""
        self.successful: bool = False
        self.negotiation_active: bool = False
        self._last_offer_received_was_acceptable = False
        self._next_constraint: Optional[AtomicConstraint] = None
        self._constraints_satisfiable = True
        self._accepts_all = False
        self._should_terminate = False

    # for string annotation reason see
    # https://www.python.org/dev/peps/pep-0484/#the-problem-of-forward-declarations
    def receive_negotiation_request(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        """
        Public function that allows other agents to propose a negoation.

        :param opponent: Agent that is proposing the negotiation.
                            Usually called with `self` as argument
        :type opponent: Agent
        :param neg_space: Negotiation space that negotiation will take place in
        :type neg_space: NegSpace
        :return: True if and only if the request for negotiation is accepted
        :rtype: bool
        """
        if self._accepts_negotiation_proposal(neg_space):
            self.opponent = opponent
            self.negotiation_active = True
            return True
        return False

    def _accepts_negotiation_proposal(self, neg_space) -> bool:
        """
        determines if the agent should accept the call for negotiation.
        Currently this just checks if the proposed negotiation
        space is equal to it's own, since this otherwise leads to inconsistencies.

        :param neg_space: the negotiation space that the proposed negotiation
                          would take place in.
        :type neg_space: NegSpace
        :return: whether the negotiation is accepted or not
        :rtype: bool
        """
        return self._neg_space == neg_space

    def _call_for_negotiation(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        """
        Send a message to opponent to request a negotiation and wait for the response.

        :param opponent: The agent self want's to negotiate with
        :type opponent: Agent
        :param neg_space: The negotiation space self want's to negotiate in
        :type neg_space: NegSpace
        :return: Whether opponent accepted the request to negotiate
        :rtype: bool
        """
        # allows us to initiate negotiations with others
        response: bool = opponent.receive_negotiation_request(self, neg_space)
        if response:
            self.opponent = opponent
        self.negotiation_active = response
        return response

    def negotiate(self, opponent: 'Agent') -> bool:
        """
        This is the entrypoint to run a negotiation, and where the main loop is located.
        `self` is assumed to have set up the negotiation before hand, meaning that it must
        have both a neotiation space and a utility function defined. This should be the case if
        the agent was created by the factory. See :doc:`/usage/agent-setup` for more information.

        :param opponent: Agent that `self` is going to negotiate with
        :type opponent: Agent
        :return: Whether the negotiation came to an agreement or not.
        :rtype: bool
        """
        # self is assumed to have setup the negotiation (including issues) beforehand
        self.negotiation_active = self._call_for_negotiation(
            opponent, self._neg_space)

        if not self.negotiation_active or not self.opponent:
            return self.successful

        next_message_to_send = Message(self.name, self.opponent.name, MessageType.EMPTY, None)
        while self.negotiation_active:
            try:
                next_message_to_send = self.generate_next_message()
            except StopIteration:
                # raised when no acceptable offers can be found
                self.send_message(opponent, self._terminate(False))
                break

            self.send_message(opponent, next_message_to_send)
            self._wait_for_response(self.opponent)

        return self.successful

    def _terminate(self, successful: bool) -> Message:
        """
        Generate the message that signals to the opporent that the negotiaion has ended and
        whether it was successful or not. If it was successful the message includes the
        offer that was accepted.

        :param successful: Whether the agents wants to terminate with agreement (True) or\
        without agreement (False)
        :type successful: bool
        :raises RuntimeError: Raised if this function is called while no negotiation is active\
        or no opponent is known.
        :return: The message that will signal to the opponent that the negotiation has ended\
        as speciffied.
        :rtype: Message
        """
        if not self.negotiation_active or not self.opponent:
            raise RuntimeError("no negotiation to terminate")

        if successful:
            self.successful = True
            self.negotiation_active = False
            return Message(self.name,
                           self.opponent.name,
                           MessageType.ACCEPT,
                           self._transcript[-1].offer)

        self.successful = False
        self.negotiation_active = False
        return Message(self.name,
                       self.opponent.name,
                       MessageType.EXIT,
                       None)

    def send_message(self, opponent: 'Agent', msg: Message) -> None:
        """
        Sends a message to the opponent, and records the communication in the transcript
        Message should be one allowed by the protocol which is defined in :ref:`msg_type`

        :param opponent: The opponent to send the message to
        :type opponent: Agent
        :param msg: The message to send
        :type msg: Message
        """
        self._record_message(msg)
        opponent.receive_message(msg)

    def _wait_for_response(self, sender: 'Agent') -> None:
        if not self.negotiation_active:
            return
        sender.send_message(self, sender.generate_next_message())

    def _record_message(self, msg: Message) -> None:
        """
        appends message to transcript

        :param msg: The message to be appended
        :type msg: Message
        """
        self._transcript.append(msg)

    def receive_message(self, msg: Message) -> None:
        """
        Main entry point for other agents to send messages to `self`.
        records the message in the transcript, parses the message
        so the engine can do the reasoing next.

        :param msg: Message to be parsed
        :type msg: Message
        """
        self._record_message(msg)
        self._parse_response(msg)

    def _parse_response(self, response: Message):
        """
        Parse a recieved message. If the message was either acceptance
        or termination we terminate the negotiation loop appropriately
        otherwise, if the message included a constraint we incorporate it
        and check if we can accept the received proposal.

        :param response: The message to be parsed
        :type response: Message
        """
        if response.type_ == MessageType.EMPTY:
            return

        if response.is_acceptance():
            self.negotiation_active = False
            self.successful = True
            return

        if response.is_termination():
            self.negotiation_active = False
            self.successful = False
            return

        if response.constraint:
            self._constraints_satisfiable = self._engine.add_constraint(response.constraint)

        if not response.offer:
            raise RuntimeError(f"Malformed message: {response}")

        if self.accepts(response.offer):
            self._last_offer_received_was_acceptable = True
            return

        self._next_constraint = self._engine.find_violated_constraint(response.offer)

    def _should_exit(self) -> bool:
        """
        Determine if we should end the negotiation without agreement.
        currently the only triger for this is when the engine can't find
        new proposals, but allows arbitrary logic.

        :raises RuntimeWarning: Raised if the engine is not properly \
            initialised, or no negotiation is active.
        :return: True if and only if the agent should terminate unsucessfully
        :rtype: bool
        """
        if not self._engine:
            raise RuntimeWarning("Engine was not initialised.")

        return not self._engine.can_continue()

    def generate_next_message(self) -> Message:
        """
        Generates the next message to be sent in a negotiation.
        Generates acceptance or termination message if appropriate,
        otherwise asks engine to generate new offer and sends message
        containing that offer.

        :raises RuntimeError: Raised if no negotiation is active
        :return: The message to be sent back
        :rtype: Message
        """

        # we should never get here if we don't have an opponent
        if not self.negotiation_active:
            raise RuntimeError("Tried to generate next message when no negotiation active")

        if not self.opponent:
            raise RuntimeError("Tried to generate next message when no opponent was known")

        if self._last_offer_received_was_acceptable:
            return self._terminate(True)

        if self._should_exit():
            return self._terminate(False)


        try:
            return Message(self.name,
                           self.opponent.name,
                           MessageType.OFFER,
                           self._engine.generate_offer(),
                           self._next_constraint)
        except StopIteration:
            # weren't able to come up with acceptable offer so terminate anyway
            return self._terminate(False)

    def accepts(self, offer: Offer) -> bool:
        """
        Determines whether an offer is acceptable or not. Mostly just a passthrough
        to the engine who does th4e actual reasoning.

        :param offer: The offer to consider
        :type offer: Offer
        :return: true if the agent finds the offer acceptable
        :rtype: bool
        """
        return self._engine.accepts(offer)

    def add_utilities(self, new_utils: Dict[str, float]) -> bool:
        """
        Adds new utilities to the knowledge base so the engine can
        reason about them properly. Returns False if adding the utility
        makes the current negotiation impossible.

        :param new_utils: New utility rules to be added
        :type new_utils: Dict[str, float]
        :return: Whether a solution is still possible according to the agent.
        :rtype: bool
        """
        return self._engine.add_utilities(new_utils)

    def set_utilities(self, new_utilities: Dict[str, float]) -> bool:
        """
        Overrides utilities int the knowledge base. Returns False if adding
        the utility makes the current negotiation impossible.

        :param new_utils: New utility rules
        :type new_utils: Dict[str, float]
        :return: Whether a solution is still possible according to the agent.
        :rtype: bool
        """
        return self._engine.set_utilities(new_utilities)

    def __repr__(self) -> str:
        return self.name
