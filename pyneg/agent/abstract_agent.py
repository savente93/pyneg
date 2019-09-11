# type: ignore
from typing import Dict, List, Optional

from pyneg.comms import Message, Offer, AtomicConstraint
from pyneg.types import NegSpace
from pyneg.engine import AbstractEngine

class AbstractAgent:
    def __init__(self):
        self.name: str = ""
        self._transcript: List[Message] = []
        self._max_rounds: int = 0
        self._neg_space: NegSpace = {}
        self._engine: AbstractEngine = AbstractEngine()
        self._absolute_reservation_value: float = -(2.0 ** 31)
        self.opponent: Optional[AbstractAgent] = None
        self._type = ""
        self.successful: bool = False
        self.negotiation_active: bool = False
        self._last_offer_received_was_acceptable = False
        self._next_constraint: Optional[AtomicConstraint] = None
        self._constraints_satisfiable = True

    def receive_negotiation_request(self, opponent: 'AbstractAgent', neg_space: NegSpace) -> bool:
        raise NotImplementedError()

    def _accepts_negotiation_proposal(self, neg_space) -> bool:
        raise NotImplementedError()

    def _call_for_negotiation(self, opponent: 'AbstractAgent', neg_space: NegSpace) -> bool:
        raise NotImplementedError()

    # to be set by the factory
    def _should_exit(self) -> bool:
        raise NotImplementedError()

    def negotiate(self, opponent: 'AbstractAgent') -> bool:
        raise NotImplementedError()

    def _terminate(self, successful: bool) -> Message:
        raise NotImplementedError()

    def send_message(self, opponent: 'AbstractAgent', msg: Message) -> None:
        raise NotImplementedError()

    def wait_for_response(self, sender: 'AbstractAgent') -> None:
        raise NotImplementedError()

    def _record_message(self, msg: Message) -> None:
        raise NotImplementedError()

    def receive_message(self, msg: Message) -> None:
        raise NotImplementedError()

    def _parse_response(self, response):
        raise NotImplementedError()

    def _generate_next_message(self) -> Message:
        raise NotImplementedError()

    def _accepts(self, offer: Offer) -> bool:
        raise NotImplementedError()

    def add_utilities(self, new_utils: Dict[str, float]) -> bool:
        raise NotImplementedError()

    def set_utilities(self, new_utils: Dict[str, float]) -> bool:
        raise NotImplementedError()
