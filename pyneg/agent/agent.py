from typing import Dict, List, Optional

from pyneg.comms import Message, Offer, AtomicConstraint
from pyneg.engine import AbstractEngine, Engine
from pyneg.types import NegSpace, MessageType
from pyneg.agent.abstract_agent import AbstractAgent


class Agent(AbstractAgent):
    def __init__(self):
        # setup all the attributes but don't init them
        # All of that is done by the factory
        self.name: str = ""
        self._transcript: List[Message] = []
        self._max_rounds: int = 0
        self._neg_space: NegSpace = {}
        self._engine: Engine = AbstractEngine()
        self._absolute_reservation_value: float = -(2.0 ** 31)
        self.opponent: Agent = AbstractAgent()
        self._type = ""
        self.successful: bool = False
        self.negotiation_active: bool = False
        self._last_offer_was_acceptable = False
        self._next_constraint: Optional[AtomicConstraint] = None

    # for string annotation reason see
    # https://www.python.org/dev/peps/pep-0484/#the-problem-of-forward-declarations
    def receive_negotiation_request(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        # allows others to initiate negotiations with us
        # only accept if we're talking about the same things
        if self._accepts_negotiation_proposal(neg_space):
            self.opponent = opponent
            return True
        else:
            return False

    def _accepts_negotiation_proposal(self, neg_space) -> bool:
        return self._neg_space == neg_space

    def _call_for_negotiation(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        # allows us to initiate negotiations with others
        response: bool = opponent.receive_negotiation_request(self, neg_space)
        if response:
            self.opponent = opponent
        return response

    # to be set by the factory
    def _should_exit(self) -> bool:
        raise NotImplementedError()

    def negotiate(self, opponent: 'Agent') -> bool:
        # self is assumed to have setup the negotiation (including issues) beforehand
        self.negotiation_active = self._call_for_negotiation(
            opponent, self._neg_space)

        next_message_to_send = Message(self.name, self.opponent.name, MessageType.empty, None)
        while self.negotiation_active:
            try:
                next_message_to_send = self._generate_next_message()
            except StopIteration:
                # raised when no acceptable offers can be found
                self.send_message(opponent, self._terminate(False))
                break

            self.send_message(opponent, next_message_to_send)
            self.wait_for_response(opponent)

        return self.successful

    def _terminate(self, successful: bool) -> Message:
        if not self.negotiation_active:
            raise RuntimeError("no negotiation to terminate")

        if successful:
            self.successful = True
            self.negotiation_active = False
            return Message(self.name,
                           self.opponent.name,
                           MessageType.accept,
                           self._transcript[-1].offer)
            # self.send_message(self.opponent, acceptance_message)
        else:
            self.successful = False
            self.negotiation_active = False
            return Message(self.name,
                           self.opponent.name,
                           MessageType.terminate,
                           None)
            # self.send_message(self.opponent, termination_message)

    def send_message(self, opponent: 'Agent', msg: Message) -> None:
        self._record_message(msg)
        opponent.receive_message(msg)

    def wait_for_response(self, sender: 'Agent') -> None:
        response = sender._generate_next_message()
        if response:
            self.receive_message(response)

    def _record_message(self, msg: Message) -> None:
        self._transcript.append(msg)

    def receive_message(self, msg: Message) -> None:
        self._record_message(msg)
        self._parse_response(msg)

    def _parse_response(self, response):
        if response.is_acceptance():
            self.negotiation_active = False
            self.successful = True

        if response.is_termination():
            self.negotiation_active = False
            self.successful = False

        if response.constraint:
            self._constraints_satisfiable = self._engine.add_constraint(response.constraint)

        if self._accepts(response.offer):
            self._last_offer_was_acceptable = True

        self._next_constraint = self._engine.find_violated_constraint(response.offer)


    def _generate_next_message(self) -> Message:
        # this check is only for the type lining
        # we should never get here if we don't have an opponent
        if not self.opponent or not self.negotiation_active:
            return Message(self.name, self.opponent.name, MessageType.empty, None)

        if self._should_exit():
            return self._terminate(False)

        if self._last_offer_was_acceptable:
            return self._terminate(True)

        return Message(self.name, self.opponent.name, MessageType.offer, self._engine.generate_offer(),
                       self._next_constraint)

    def _accepts(self, offer: Offer) -> bool:
        return self._engine.calc_offer_utility(offer) >= self._absolute_reservation_value and self._constraints_satisfiable

    def add_utilities(self, new_utils: Dict[str, float]) -> bool:
        return self._engine.add_utilities(new_utils)

    def set_utilities(self, new_utils: Dict[str, float]) -> bool:
        return self._engine.set_utilities(new_utils)
