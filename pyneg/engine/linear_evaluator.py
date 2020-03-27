"""
A simple evaluator that calculates the utility of an offer
assuming :ref:`linear-additivity`
"""

from typing import Dict, Set

from pyneg.comms import Offer, AtomicConstraint
from pyneg.types import AtomicDict
from pyneg.utils import atom_from_issue_value

from .engine import Evaluator
from .strategy import Strategy


class LinearEvaluator(Evaluator):
    """
    Evaluates offers using linear additive calculations.
    (see :ref:`linear-additivity`)
    Utilities should be a utility function represented
    as an AtomicDict, issue weights should be a distribution over the
    issues and non_agreement_cost should be the cost of unsuccessfully
    terminating the negotiation.
    """

    def __init__(self, utilities: AtomicDict,
                 issue_weights: Dict[str, float],
                 non_agreement_cost: float):
        super().__init__()
        self.utilities = utilities
        self.issue_weights = issue_weights
        self.non_agreement_cost = non_agreement_cost

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

        return True

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils
        return True

    def calc_assignment_util(self, issue: str, value: str) -> float:
        """
        calculates the utility gained from a perticular signed assignment
        asignements with unknown utilities are assigned 0 utility

        >>> print(self.utilities)
        {"boolean_False": -10, "boolean_True":10, "integer_3": 100}
        >>> self.calc_assignment_util("boolean","False")
        -10
        >>> self.calc_assignment_util("unknown","unknown")
        0

        :param issue: the issue the assignment is associated with
        :type issue: str
        :param value: the value of the potential assignement
        :type value: str
        :return: the utility of the experiement
        :rtype: float
        """
        chosen_atom = atom_from_issue_value(issue, value)
        if chosen_atom in self.utilities.keys():
            return self.issue_weights[issue] * \
                   self.utilities[chosen_atom]

        return 0

    def calc_offer_utility(self, offer: Offer) -> float:
        """
        Calculates the utility of a full offer. In this implementation
        this is simply the dot product of the utility of all the asignements
        with their associated issue weights

        :param offer: The offer to calculate the utility of
        :type offer: Offer
        :return: the utility the given offer is worth
        :rtype: float
        """
        score = 0.0
        for issue in offer.get_issues():
            chosen_value = offer.get_chosen_value(issue)
            score += self.calc_assignment_util(issue, chosen_value)
        return score

    def calc_strat_utility(self, strat: Strategy) -> float:
        """
        Generalisation of an offer but works similarly. calculates the
        expceted utility under the strategy distribution. see
        :class:`Strategy` for more information.

        :param strat: the strategy to calculate the utility of
        :type strat: Strategy
        :return: expected utility under the given strategy with \
            current knowledge base
        :rtype: float
        """
        score = 0.0
        for issue in strat.get_issues():
            for value, prob in strat.get_value_dist(issue).items():
                atom = atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    score += self.issue_weights[issue] * \
                             self.utilities[atom] * prob

        return score

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
