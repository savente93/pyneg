from typing import Dict, List, Optional

from pyneg.comms import Message, Offer
from pyneg.types import NegSpace
from pyneg.agent.agent import Agent


class AbstractAgent(Agent):
    def __init__(self):
        pass

    def receive_negotiation_request(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        raise NotImplementedError()

    def _accepts_negotiation_proposal(self, neg_space) -> bool:
        raise NotImplementedError()

    def _call_for_negotiation(self, opponent: 'Agent', neg_space: NegSpace) -> bool:
        raise NotImplementedError()

    # to be set by the factory
    def _should_exit(self) -> bool:
        raise NotImplementedError()

    def negotiate(self, opponent: 'Agent') -> bool:
        raise NotImplementedError()

    def _terminate(self, successful: bool) -> Message:
        raise NotImplementedError()

    def send_message(self, opponent: 'Agent', msg: Message) -> None:
        raise NotImplementedError()

    def wait_for_response(self, sender: 'Agent') -> None:
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
