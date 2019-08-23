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
from abstract_agent import AbstractAgent, Verbosity, NegSpace


class AbstractLinearAgent(AbstractAgent):
    def __init__(self,
                 name: str,
                 neg_space: NegSpace,
                 utilities: Dict[str, float],
                 reservation_value: float,
                 issue_weights: Optional[Dict[str, float]],
                 max_rounds: Optional[int] = None,
                 verbose: Verbosity = Verbosity.none):

        super().__init__(name, neg_space, utilities, reservation_value, verbose)
        self.setup_issue_weights(issue_weights)

    def setup_issue_weights(self, issue_weights: Optional[Dict[str, float]]) -> None:
        if issue_weights:
            self.issue_weights:  Dict[str, float] = issue_weights
        elif self.neg_space:
            self.issue_weights = {}
            for issue in self.neg_space.keys():
                self.issue_weights[issue] = 1/len(self.neg_space.keys())

    def setup_negotiation(self, neg_space: NegSpace) -> None:
        raise NotImplementedError()

    def calc_offer_utility(self, offer: Offer) -> float:
        raise NotImplementedError()

    def generate_offer(self) -> Optional[Offer]:
        raise NotImplementedError()
