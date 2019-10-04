from typing import Dict, List, Optional

from pyneg.comms import Message, Offer, AtomicConstraint
from pyneg.engine import AbstractEngine, Engine
from pyneg.types import NegSpace, MessageType
from pyneg.agent.abstract_agent import AbstractAgent


class Agent(AbstractAgent):
    def __init__(self):
        # setup all the attributes but don't init them
        # All of that is done by the factory
        super().__init__()

    # for string annotation reason see
    # https://www.python.org/dev/peps/pep-0484/#the-problem-of-forward-declarations
    def receive_negotiation_request(self, opponent: AbstractAgent, neg_space: NegSpace) -> bool:
        # allows others to initiate negotiations with us
        # only accept if we're talking about the same things
        if self._accepts_negotiation_proposal(neg_space):
            self.opponent = opponent
            self.negotiation_active = True
            return True
        else:
            return False

    def _accepts_negotiation_proposal(self, neg_space) -> bool:
        return self._neg_space == neg_space

    def _call_for_negotiation(self, opponent: AbstractAgent, neg_space: NegSpace) -> bool:
        # allows us to initiate negotiations with others
        response: bool = opponent.receive_negotiation_request(self, neg_space)
        if response:
            self.opponent = opponent
        self.negotiation_active = response
        return response

    def negotiate(self, opponent: AbstractAgent) -> bool:
        # self is assumed to have setup the negotiation (including issues) beforehand
        self.negotiation_active = self._call_for_negotiation(
            opponent, self._neg_space)

        if not self.negotiation_active or not self.opponent:
            return self.successful

        next_message_to_send = Message(self.name, self.opponent.name, MessageType.EMPTY, None)
        while self.negotiation_active:
            try:
                next_message_to_send = self._generate_next_message()
            except StopIteration:
                # raised when no acceptable offers can be found
                self.send_message(opponent, self._terminate(False))
                break

            self.send_message(opponent, next_message_to_send)
            self._wait_for_response(self.opponent)

        return self.successful

    def _terminate(self, successful: bool) -> Message:
        if not self.negotiation_active:
            raise RuntimeError("no negotiation to terminate")

        if successful:
            self.successful = True
            self.negotiation_active = False
            return Message(self.name,
                           self.opponent.name,
                           MessageType.ACCEPT,
                           self._transcript[-1].offer)
            # self.send_message(self.opponent, acceptance_message)
        else:
            self.successful = False
            self.negotiation_active = False
            return Message(self.name,
                           self.opponent.name,
                           MessageType.EXIT,
                           None)
            # self.send_message(self.opponent, termination_message)

    def send_message(self, opponent: AbstractAgent, msg: Message) -> None:
        self._record_message(msg)
        opponent.receive_message(msg)

    def _wait_for_response(self, sender: AbstractAgent) -> None:
        if not self.negotiation_active:
            return
        sender.send_message(self,sender._generate_next_message())

    def _record_message(self, msg: Message) -> None:
        self._transcript.append(msg)

    def receive_message(self, msg: Message) -> None:
        self._record_message(msg)
        self._parse_response(msg)

    def _parse_response(self, response):
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


        if self._accepts(response.offer):
            self._last_offer_received_was_acceptable = True
            return

        self._next_constraint = self._engine.find_violated_constraint(response.offer)

    def _should_exit(self) -> bool:
        return not self._engine.can_continue()
        # try:
        #     if not self._constraints_satisfiable:
        #         return True
        #
        #     if self._transcript[-1].is_termination():
        #         return True
        #
        #     if self._transcript[-1].sender_name != self.name:
        #         util = self._engine.calc_offer_utility(self._transcript[-2].offer)
        #     else:
        #         util = self._engine.calc_offer_utility(self._transcript[-1].offer)
        #     return util <= self._absolute_reservation_value
        # except IndexError:
        #     # shouldn't terminate if we haven't generated any offers
        #     return False

    def _generate_next_message(self) -> Message:
        # this check is only for the type lining
        # we should never get here if we don't have an opponent
        if not self.opponent or not self.negotiation_active:
            return Message(self.name, self.opponent.name, MessageType.EMPTY, None)

        if self._last_offer_received_was_acceptable:
            return self._terminate(True)

        if self._should_exit():
            return self._terminate(False)


        try:
            return Message(self.name, self.opponent.name, MessageType.OFFER, self._engine.generate_offer(),
                       self._next_constraint)
        except StopIteration:
            # weren't able to come up with acceptable offer so terminate anyway
            return self._terminate(False)

    def _accepts(self, offer: Offer) -> bool:
        return self._engine.accepts(offer)

    def add_utilities(self, new_utils: Dict[str, float]) -> bool:
        return self._engine.add_utilities(new_utils)

    def set_utilities(self, new_utilities: Dict[str, float]) -> bool:
        return self._engine.set_utilities(new_utilities)

    def __repr__(self) -> str:
        return self.name
