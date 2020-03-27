"""
This module defines the :class:`ProblogEvaluator` class.
"""
from typing import Dict, List, Set

from problog import get_evaluatable
from problog.program import PrologString

from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from pyneg.types import NegSpace
from pyneg.utils import atom_from_issue_value
from .engine import Evaluator
from .strategy import Strategy


class ProblogEvaluator(Evaluator):
    """
    This evaluator uses ProbLog to calculate the utility of offers.
    That means that it can deal with probabalistic as well as deterministic
    knowledge bases and use them correctly to infer consequences.
    This is however, much slower than the other classes. The knowledge base
    should be represented as valid ProbLog statements see
    https://dtai.cs.kuleuven.be/problog/ for more information.
    """
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 knowledge_base: List[str]):
        super().__init__()
        self.utilities = utilities
        self.knowledge_base = knowledge_base
        self.neg_space = neg_space
        self.non_agreement_cost = non_agreement_cost

    def calc_probabilities_of_utilities(self, offer: Offer) -> Dict[str, float]:
        """
        Uses ProbLog and the known knowledge_base to calculate the probability
        of each of the known utilities to occur so we can use it to calculate the
        expected utility of an offer.

        :param offer: The offer you want to calculate the utility of
        :type offer: Offer
        :return: A dictionary with known utilities as keys and the probability \
            they will be fufilled as values.
        :rtype: Dict[str, float]
        """
        model = self.compile_problog_model(offer)
        probability_of_facts = {str(atom): util for atom, util in
                                get_evaluatable("sdd").create_from(
                                    PrologString(model)).evaluate().items()}

        return probability_of_facts

    def compile_problog_model(self, offer: Offer) -> str:
        """
        Compile the offer, knowledge base and known utilities into a string
        representing a valid ProbLog model.

        :param offer: The offer that needs to be incoprated into the model.
        :type offer: Offer
        :return: A string representation of the model including knowledge base and utilities
        :rtype: str
        """
        decision_facts_string = offer.get_problog_dists()

        query_string = ""
        for util_atom in self.utilities.keys():
            # we shouldn't ask problog for facts that we currently have no rules for
            # like we might not have after new issues are set so we'll skip those
            if any([util_atom in rule for rule in self.knowledge_base]) or any(
                    [util_atom in atom for atom in self.utilities.keys()]):
                query_string += "query({utilFact}).\n".format(utilFact=util_atom)

        kb_string = "\n".join(self.knowledge_base) + "\n"

        return decision_facts_string + kb_string + query_string

    def calc_offer_utility(self, offer: Offer) -> float:
        probability_of_utilities = self.calc_probabilities_of_utilities(offer)
        total_util = 0.0
        for atom, prob in probability_of_utilities.items():
            total_util += prob * self.utilities[atom]

        return total_util

    def calc_strat_utility(self, strat: Strategy) -> float:
        """
        Calculate the expected utility of a strategy, meaning the expected
        utility of an offer that is sampled from this strattegy under the current
        knowledge base.

        :param strat: The strat to calculate the expected utility.
        :type strat: Strategy
        :return: The expected utility of the strategy under the current knowledge base \
            and utilities.
        :rtype: float
        """
        score = 0.0
        for issue in strat.get_issues():
            for value, prob in strat.get_value_dist(issue).items():
                atom = atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    score += self.utilities[atom] * prob

        return score

    def calc_assignment_util(self, issue: str, value: str) -> float:
        atom = atom_from_issue_value(issue, value)
        if atom in self.utilities.keys():
            return self.utilities[atom]

        return 0.0

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils
        return True

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        print("""WARNING: attempting to use a constraint mechanism
            with non constraint aware system.
            add_constraint called in {self.class.__name__}""")
        return True

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                add_constraints called in {self.class.__name__}""")
        return True
