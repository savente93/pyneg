from numpy import isclose
from re import search, sub
from message import Message, MessageType
from numpy.random import choice
import subprocess as sp
from os import remove, getpid
from os.path import join, abspath, dirname
from problog.program import PrologString
from problog import get_evaluatable
from enum import IntEnum
from offer import Offer
from typing import Dict, Tuple, List, Optional, cast

NestedDict = Dict[str, Dict[str, float]]
NegSpace = Dict[str, List[str]]
standard_max_rounds = 200


class Verbosity(IntEnum):
    none = 0
    messages = 1
    reasoning = 2
    debug = 3


class AbstractAgent:
    def __init__(self,
                 name: str,
                 neg_space: NegSpace,
                 utilities: Dict[str, float],
                 reservation_value: float,
                 max_rounds: Optional[int] = None,
                 verbose: Verbosity = Verbosity.none):
        self.verbose: Verbosity = verbose

        if not max_rounds:
            self.max_rounds: int = standard_max_rounds
        else:
            self.max_rounds = max_rounds

        self.opponent_name: str = ""
        self.non_agreement_cost: float = -(2 ** 31)  # just a big number
        self.relative_reservation_value: float = reservation_value
        self.absolute_reservation_value: float = (
            2 ** 31)  # will get overwriten in child classes
        self.successful: bool = False
        self.negotiation_active: bool = False
        self.strat_name: str = "Abstract"
        self.agent_name: str = name
        self.transcript: List[Message] = []
        self.utilities: Dict[str, float] = utilities
        self.neg_space: NegSpace = neg_space
        self.opponent: Optional[AbstractAgent] = None
        self.next_message_to_send: Optional[Message] = None
        self.max_utility_by_issue: Dict[str, float] = {}

    def receive_negotiation_request(self, opponent: AbstractAgent, neg_space: NegSpace) -> bool:
        # allows others to initiate negotiations with us
        # we always accept calls for negotiation if we can init properly
        try:
            self.setup_negotiation(neg_space)
            self.opponent = opponent
            self.opponent_name = opponent.agent_name
            return True
        except:
            # something went wrong setting up so reject request
            print("{} failed to setup negotiation properly".format(self.agent_name))
            return False

    def call_for_negotiation(self, opponent: Optional[AbstractAgent], neg_space: NegSpace) -> bool:
        if not opponent:
            return False
        else:
            opponent = cast(AbstractAgent, opponent)

        # allows us to initiate negotiations with others
        response: bool = opponent.receive_negotiation_request(
            self, neg_space)
        if response:
            self.opponent = opponent
        return response

    def should_terminate(self) -> bool:
        return len(self.transcript) > self.max_rounds

    def negotiate(self, opponent: AbstractAgent) -> bool:
        if not self.neg_space:
            raise RuntimeError(
                "Cannot negotiate before negotiation space is initialised")
        # self is assumed to have setup the negotiation (including issues) beforehand
        self.negotiation_active = self.call_for_negotiation(
            opponent, self.neg_space)

        # make initial offer
        while self.negotiation_active:
            self.next_message_to_send = self.generate_next_message_from_transcript()
            if self.next_message_to_send:
                self.send_message(opponent, self.next_message_to_send)
                self.wait_for_response(opponent)

        return self.successful

    def send_message(self, opponent: AbstractAgent, msg: Message) -> None:
        self.record_message(msg)
        if self.verbose >= Verbosity.messages:
            print("{} is sending {}".format(self.agent_name, msg))
        opponent.receive_message(msg)

    def wait_for_response(self, sender: AbstractAgent) -> None:
        response = sender.generate_next_message_from_transcript()
        if response:
            self.receive_message(response)

    def record_message(self, msg: Message) -> None:
        self.transcript.append(msg)

    def receive_message(self, msg: Message) -> None:
        if self.verbose >= Verbosity.messages:
            print("{}: received message: {}".format(self.agent_name, msg))
        self.record_message(msg)

    def generate_next_message_from_transcript(self) -> Optional[Message]:
        try:
            last_message: Message = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self.generate_offer_message()

        if last_message.is_acceptance():
            self.negotiation_active = False
            self.successful = True
            return None

        if last_message.is_termination():
            self.negotiation_active = False
            self.successful = False
            return None

        if self.should_terminate():
            self.negotiation_active = False
            self.successful = False
            return Message(self.agent_name, self.opponent_name, MessageType.terminate, last_message.offer)

        if self.accepts(last_message.offer):
            self.negotiation_active = False
            self.successful = True
            return Message(self.agent_name, self.opponent_name, MessageType.accept, last_message.offer)

        return self.generate_offer_message()

    def accepts(self, offer: Optional[Offer]) -> bool:
        if self.verbose >= Verbosity.reasoning:
            print("{}: considering \n{}".format(
                self.agent_name, offer))

        if not offer:
            return False

        util: float = self.calc_offer_utility(offer)

        if self.verbose >= Verbosity.reasoning:
            if self.verbose >= Verbosity.debug:
                print("absolute reservation value: {}\n offer utility: {}".format(
                    self.absolute_reservation_value, util))
            if util >= self.absolute_reservation_value:
                print("{}: offer is acceptable\n".format(self.agent_name))
            else:
                print("{}: offer is not acceptable\n".format(self.agent_name))

        return util >= self.absolute_reservation_value

    def generate_offer_message(self) -> Optional[Message]:
        offer: Optional[Offer] = self.generate_offer()
        if not offer:
            termination_message: Message = Message(
                self.agent_name, self.opponent_name, MessageType.terminate, None)
            self.record_message(termination_message)
            return termination_message
        else:
            return Message(self.agent_name, self.opponent_name, type_=MessageType.offer, offer=offer)

    def add_utilities(self, new_utils: Dict[str, float]) -> None:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

    def index_max_utilities(self) -> None:
        if self.verbose >= Verbosity.debug:
            print("{} is indexing max utilities".format(self.agent_name))

        self.max_utility_by_issue = {}
        for issue in self.neg_space.keys():
            max_issue_util: float = -(2**31)
            for value in self.neg_space[issue]:
                atom = Offer.atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    util = self.utilities[atom]
                else:
                    util = 0

                if util > max_issue_util:
                    max_issue_util = util
                    self.max_utility_by_issue[issue] = max_issue_util

                if not issue in self.max_utility_by_issue.keys():
                    self.max_utility_by_issue[issue] = 0

        self.absolute_reservation_value = self.relative_reservation_value * self.get_max_utility()

    def get_max_utility(self) -> float:
        if self.max_utility_by_issue:
            return(sum(self.max_utility_by_issue.values()))
        else:
            return 0

    def generate_offer(self) -> Optional[Offer]:
        raise NotImplementedError()

    def setup_negotiation(self, issues: NegSpace) -> None:
        raise NotImplementedError()

    def calc_offer_utility(self, offer: Offer) -> float:
        raise NotImplementedError()
