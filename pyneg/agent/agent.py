from typing import Dict, Tuple, List, Optional, cast
from pyneg.types import NegSpace, Verbosity
from pyneg.comms import Message, MessageType, Offer
from pyneg.engine import Engine, AbstractEngine


class Agent:
    def __init__(self):
        # setup all the attributes but don't init them
        # All of that is done by the factory
        self.name: str = ""
        self.transcript: List[Message] = []
        self.max_rounds: int = 0
        self.neg_space: NegSpace = {}
        self.engine: Engine = AbstractEngine()
        self.absolute_reservation_value: float = -(2.0 ** 31)
        self.opponent: Optional[Agent] = None
        self._type = ""
        self.successful: bool = False
        self.negotiation_active: bool = False

    # for string annotation reason see
    # https://www.python.org/dev/peps/pep-0484/#the-problem-of-forward-declarations
    def receive_negotiation_request(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        # allows others to initiate negotiations with us
        # only accept if we're talking about the same things
        if self.neg_space == neg_space:
            self.opponent = opponent
            return True
        else:
            return False

    def _call_for_negotiation(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        # allows us to initiate negotiations with others
        response: bool = opponent.receive_negotiation_request(self, neg_space)
        if response:
            self.opponent = opponent
        return response

    def _should_terminate(self) -> bool:
        return len(self.transcript) > self.max_rounds

    def negotiate(self, opponent: 'Agent') -> bool:
        # self is assumed to have setup the negotiation (including issues) beforehand
        self.negotiation_active = self._call_for_negotiation(
            opponent, self.neg_space)

        while self.negotiation_active:
            next_message_to_send = self.generate_next_message()
            if next_message_to_send:
                self.send_message(opponent, next_message_to_send)
                self.wait_for_response(opponent)

        return self.successful

    def send_message(self, opponent: 'Agent', msg: Message) -> None:
        self._record_message(msg)
        opponent.receive_message(msg)

    def wait_for_response(self, sender: 'Agent') -> None:
        response = sender._generate_next_message()
        if response:
            self.receive_message(response)

    def _record_message(self, msg: Message) -> None:
        self.transcript.append(msg)

    def receive_message(self, msg: Message) -> None:
        self._record_message(msg)

    def generate_next_message(self) -> Optional[Message]:
        # this check is only for the type lining
        # we should never get here if we don't have an opponent
        if not self.opponent:
            return None

        try:
            last_message: Message = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self._generate_offer_message(self.opponent)

        if last_message.is_acceptance():
            self.negotiation_active = False
            self.successful = True
            return None

        if last_message.is_termination():
            self.negotiation_active = False
            self.successful = False
            return None

        if self._should_terminate():
            self.negotiation_active = False
            self.successful = False
            return Message(self.name, self.opponent.name, MessageType.terminate, last_message.offer)

        if last_message.offer is None:
            raise RuntimeError(
                "Message that was supposed to be an offer message is empty")

        if self._accepts(last_message.offer):
            self.negotiation_active = False
            self.successful = True
            return Message(self.name, self.opponent.name, MessageType.accept, last_message.offer)

        return self._generate_offer_message(self.opponent)

    def _accepts(self, offer: Offer) -> bool:
        return self._calc_offer_utility(offer) >= self.absolute_reservation_value

    def _generate_offer_message(self, recipient: 'Agent') -> Message:
        try:
            offer: Offer = self._generate_offer()
        except StopIteration:
            termination_message: Message = Message(
                self.name, recipient.name, MessageType.terminate, None)
            self._record_message(termination_message)
            return termination_message

        return Message(self.name, recipient.name, type_=MessageType.offer, offer=offer)

    def add_utilities(self, new_utils: Dict[str, float]) -> None:
        self.engine.add_utilities(new_utils)

    def set_utilities(self, new_utils: Dict[str, float]) -> None:
        self.engine.set_utilities(new_utils)

    def _generate_offer(self) -> Offer:
        return self.engine.generate_offer()

    def _calc_offer_utility(self, offer: Offer) -> float:
        return self.engine.calc_offer_utility(offer)
