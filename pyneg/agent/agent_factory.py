"""
This module defines all of the factory methods for creating different types of agents.
Available factories:
- make_linear_concession_agent
- make_linear_random_agent
- make_random_agent
- make_constrained_linear_concession_agent
- make_constrained_linear_random_agent
"""
# pylint: disable=protected-access
# because different kinds of agents need different kinds of engines and other parameters,
# this had to be done by factories instead of init functions.
# this is why we disable protected-access warnings for htis file


from typing import Dict, List, Optional, Set, Union

from numpy import isclose

from pyneg.comms import AtomicConstraint
from pyneg.engine import (ConstrainedEnumGenerator, ConstrainedLinearEvaluator,
                          ConstrainedRandomGenerator, Engine, EnumGenerator,
                          Evaluator, Generator, LinearEvaluator,
                          ProblogEvaluator, RandomGenerator)
from pyneg.types import NegSpace
from pyneg.utils import issue_value_tuple_from_atom, nested_dict_from_atom_dict

from . import Agent, ConstrainedAgent

STANDARD_MAX_ROUNDS = 200



def estimate_max_linear_utility(utilities: Dict[str, float]) -> float:
    """
    This function estimates the maximum utility of a linear additive utility function.
    It is used to calculate the absolute reservation value from the percentile that is
    given to the factories. This only works for linear additive functions and as such
    cannot handle knowledge bases.

    :param utilities: The utility function repsented by an atomic dictionary
    :type utilities: Dict[str, float]
    :return: the maximum utility possible under the utility function
    :rtype: float
    """
    nested_utilities = nested_dict_from_atom_dict(utilities)
    max_utility_by_issue = {issue: -(10.0**10) for issue in nested_utilities}
    for issue in nested_utilities:
        for _, util in nested_utilities[issue].items():
            if max_utility_by_issue[issue] < util:
                max_utility_by_issue[issue] = util

    return sum(max_utility_by_issue.values())


def make_linear_concession_agent(
        name: str,
        neg_space: NegSpace,
        utilities: Dict[str, float],
        reservation_value: float,
        non_agreement_cost: float,
        issue_weights: Optional[Dict[str, float]] = None) -> Agent:
    """
    This function constructs a linear constraint. That means that the resulting agent,
    calculates the utility of an offer with linear additive functions using numpy as a backend.
    (see :ref:`linear-additivity`) It uses concession as it's statagy
    meaning that it uses a breath first search to discover offers
    and simply offers them in order of preference.

    :param name: Name of the agent, mainly for logging purposes
    :type name: str
    :param neg_space: The negotiation space the negotiation will take place in
    :type neg_space: NegSpace
    :param utilities: The utility function of the agent represented as an atomic dictionary
    :type utilities: Dict[str, float]
    :param reservation_value: The lowest amount of utility the agent still finds acceptable, \
        expressed as a percentage of the maximum utility
    :type reservation_value: float
    :param non_agreement_cost: The utility awarded to the agent if the negotiation is unsuccessful
    :type non_agreement_cost: float
    :param issue_weights: Relative importance of the issues to the agent. Should be a distribution \
        indexed by issues. Defaults to uniform if none is provided.
    :type issue_weights: Optional[Dict[str, float]]
    :return: The agent with the correct mechanisms initialised.
    :rtype: Agent
    """
    agent = Agent()
    agent.name = name
    agent._type = "Linear Concession"
    agent._neg_space = neg_space
    agent._should_terminate = False

    if not issue_weights:
        issue_weights = {issue: 1 / len(neg_space.keys()) for issue in neg_space.keys()}

    weight_adjusted_utilities = {}
    for atom, util in utilities.items():
        issue, _ = issue_value_tuple_from_atom(atom)
        weight_adjusted_utilities[atom] = util * issue_weights[issue]


    estimate_max_utility = estimate_max_linear_utility(weight_adjusted_utilities)
    reservation_value = reservation_value * estimate_max_utility
    agent._absolute_reservation_value = reservation_value
    evaluator: Evaluator = LinearEvaluator(utilities, issue_weights, non_agreement_cost)
    generator: Generator = EnumGenerator(neg_space, utilities, evaluator, reservation_value)
    engine: Engine = Engine(generator, evaluator)
    if isclose(reservation_value, 0):
        engine._accepts_all = True

    agent._engine = engine

    return agent


def make_linear_random_agent(
        name: str,
        neg_space: NegSpace,
        utilities: Dict[str, float],
        reservation_value: float,
        non_agreement_cost: float,
        issue_weights: Optional[Dict[str, float]] = None,
        max_rounds: int = None) -> Agent:
    """
    This agent calculates utility in a linear additive way using numpy as a backend.
    it also uses numpy to generate random offers by sampling from the strategy distribution.
    This is initialised as a uniform distribution across all possible values for every issue.


    :param name: Name of the agent, mainly for logging purposes
    :type name: str
    :param neg_space: The negotiation space the negotiation will take place in
    :type neg_space: NegSpace
    :param utilities: The utility function of the agent represented as an atomic dictionary
    :type utilities: Dict[str, float]
    :param reservation_value: The lowest amount of utility the agent still finds acceptable, \
        expressed as a percentage of the maximum utility
    :type reservation_value: float
    :param non_agreement_cost: The utility awarded to the agent if the negotiation is unsuccessful
    :type non_agreement_cost: float
    :param issue_weights: Relative importance of the issues to the agent. Should be a distribution \
        Defaults to uniform if none is provided.
    :type issue_weights: Optional[Dict[str, float]]
    :param max_rounds: Maximum number of rounds the agent will try to generate an offer. \
        This is to make sure that even impossible negotiations terminate. Defaults to 200
    :type max_rounds: int, optional
    :return:  The agent with the correct mechanisms initialised.
    :rtype: Agent
    """

    agent = Agent()
    agent.name = name
    agent._type = "Linear Random"
    agent._neg_space = neg_space
    agent._should_terminate = False

    if not issue_weights:
        issue_weights = {issue: 1 / len(neg_space.keys()) for issue in neg_space.keys()}

    if not max_rounds:
        max_rounds = STANDARD_MAX_ROUNDS

    weight_adjusted_utilities = {}
    for atom, util in utilities.items():
        issue, _ = issue_value_tuple_from_atom(atom)
        weight_adjusted_utilities[atom] = util * issue_weights[issue]

    estimate_max_utility = estimate_max_linear_utility(weight_adjusted_utilities)
    reservation_value = reservation_value * estimate_max_utility

    agent._absolute_reservation_value = reservation_value
    evaluator: Evaluator = LinearEvaluator(utilities, issue_weights, non_agreement_cost)
    generator: Generator = RandomGenerator(
        neg_space,
        utilities,
        evaluator,
        non_agreement_cost,
        [],
        reservation_value,
        max_rounds)

    engine = Engine(generator, evaluator)
    if isclose(reservation_value, 0):
        engine._accepts_all = True

    agent._engine = engine

    return agent


def make_random_agent(
        name: str,
        neg_space: NegSpace,
        utilities: Dict[str, float],
        reservation_value: Union[float, int],
        non_agreement_cost: float,
        knowledge_base: List[str],
        max_rounds: int = None) -> Agent:
    """
    This agent uses ProbLog as a backend to evaluate offers. That means that it can
    handle non-linear utility functions and non trivial (probabalistic) knowledge bases.
    However this does also mean that it is relatively slow

    :param name: Name of the agent, mainly for logging purposes
    :type name: str
    :param neg_space: The negotiation space the negotiation will take place in
    :type neg_space: NegSpace
    :param utilities: The utility function of the agent represented as an atomic dictionary
    :type utilities: Dict[str, float]
    :param reservation_value: The lowest amount of utility the agent still finds acceptable, \
        expressed as a percentage of the maximum utility
    :type reservation_value: float
    :param non_agreement_cost: The utility awarded to the agent if the negotiation is unsuccessful
    :type non_agreement_cost: float
    :param knowledge_base: Any aditional rules that should be known to the agent \
        represented as a list of valid ProbLog statements.
    :type knowledge_base: List[str]
    :param max_rounds: Maximum number of rounds the agent will try to generate an offer. \
        This is to make sure that even impossible negotiations terminate. Defaults to 200
    :type max_rounds: int, optional
    :return:  The agent with the correct mechanisms initialised.
    :rtype: Agent
    """
    agent = Agent()
    agent.name = name
    agent._type = "Random"
    agent._neg_space = neg_space
    agent._should_terminate = False

    if not max_rounds:
        max_rounds = STANDARD_MAX_ROUNDS


    estimate_max_utility = estimate_max_linear_utility(utilities)
    reservation_value = reservation_value * estimate_max_utility

    agent._absolute_reservation_value = reservation_value
    evaluator: Evaluator = ProblogEvaluator(neg_space,
                                            utilities,
                                            non_agreement_cost,
                                            knowledge_base)
    generator: Generator = RandomGenerator(
        neg_space,
        utilities,
        evaluator,
        reservation_value,
        knowledge_base,
        reservation_value, max_rounds)

    engine = Engine(generator, evaluator)
    if isclose(reservation_value, 0):
        engine._accepts_all = True
    agent._engine = engine

    return agent


def make_constrained_linear_concession_agent(
        name: str,
        neg_space: NegSpace,
        utilities: Dict[str, float],
        reservation_value: float, non_agreement_cost: float,
        initial_constraints: Optional[Set[AtomicConstraint]] = None,
        issue_weights: Optional[Dict[str, float]] = None,
        auto_constraints=True) -> ConstrainedAgent:
    """
    This function constructs a linear constraint agent. That means that the resulting agent,
    calculates the utility of an offer with linear additive functions using numpy as a backend.
    (see :ref:`linear-additivity`) It uses concession as it's statagy
    meaning that it uses a breath first search to discover offers
    and simply offers them in order of preference. In addition both the search
    and evaluation procedures know how to correctly handle any constraints.
    These can be givin to the agent apriori, deduced automatically from the
    utility function or received from the opponent.

    :param name: Name of the agent, mainly for logging purposes
    :type name: str
    :param neg_space: The negotiation space the negotiation will take place in
    :type neg_space: NegSpace
    :param utilities: The utility function of the agent represented as an atomic dictionary
    :type utilities: Dict[str, float]
    :param reservation_value: The lowest amount of utility the agent still finds acceptable, \
        expressed as a percentage of the maximum utility
    :type reservation_value: float
    :param non_agreement_cost: The utility awarded to the agent if the negotiation is unsuccessful
    :type non_agreement_cost: float
    :param initial_constraints: A set containing all constraints known to the agent \
        at the beginning defaults to empty if none are given.
    :type initial_constraints: Optional[Set[AtomicConstraint]]
    :param issue_weights: Relative importance of the issues to the agent. Should be a distribution \
        indexed by issues. Defaults to uniform if none is provided.
    :type issue_weights: Optional[Dict[str, float]]
    :param auto_constraints: Whether the agent should attempt to automatically deduce \
        whether constraints can be created. ONly works for linear additive utility functions.
        defaults to True
    :type auto_constraints: bool
    :return: The agent with the correct mechanisms initialised.
    :rtype: ConstrainedAgent
    """

    agent = ConstrainedAgent()
    agent.name = name
    agent._type = "Constrained Linear Concession"
    agent._neg_space = neg_space
    agent._should_terminate = False

    if not issue_weights:
        issue_weights = {
            issue: 1 / len(neg_space) for issue in neg_space}

    if not initial_constraints:
        initial_constraints = set()

    weight_adjusted_utilities = {}
    for atom, util in utilities.items():
        issue, _ = issue_value_tuple_from_atom(atom)
        weight_adjusted_utilities[atom] = util * issue_weights[issue]

    estimate_max_utility = estimate_max_linear_utility(weight_adjusted_utilities)
    reservation_value = reservation_value * estimate_max_utility
    constr_value = -2 * estimate_max_utility
    agent._absolute_reservation_value = reservation_value
    evaluator: Evaluator = ConstrainedLinearEvaluator(
        utilities,
        issue_weights,
        non_agreement_cost,
        constr_value,
        initial_constraints)
    generator: Generator = ConstrainedEnumGenerator(
        neg_space,
        utilities,
        evaluator,
        reservation_value,
        constr_value,
        initial_constraints,
        auto_constraints=auto_constraints)

    engine: Engine = Engine(generator, evaluator)
    if isclose(reservation_value, 0):
        engine._accepts_all = True
    agent._engine = engine

    return agent


def make_constrained_linear_random_agent(
        name: str,
        neg_space: NegSpace,
        utilities: Dict[str, float],
        reservation_value: float,
        non_agreement_cost: float,
        knowledge_base: List[str],
        issue_weights: Optional[Dict[str, float]] = None,
        initial_constraints: Optional[Set[AtomicConstraint]] = None,
        max_rounds: int = None,
        auto_constraints=True) -> ConstrainedAgent:
    """
    [summary]

    :param name: Name of the agent, mainly for logging purposes
    :type name: str
    :param neg_space: The negotiation space the negotiation will take place in
    :type neg_space: NegSpace
    :param utilities: The utility function of the agent represented as an atomic dictionary
    :type utilities: Dict[str, float]
    :param reservation_value: The lowest amount of utility the agent still finds acceptable, \
        expressed as a percentage of the maximum utility
    :type reservation_value: float
    :param non_agreement_cost: The utility awarded to the agent if the negotiation is unsuccessful
    :type non_agreement_cost: float
    :param issue_weights: Relative importance of the issues to the agent. Should be a distribution \
        Defaults to uniform if none is provided.
    :type issue_weights: Optional[Dict[str, float]]
    :param knowledge_base: Any aditional rules that should be known to the agent \
        represented as a list of valid ProbLog statements.
    :type knowledge_base: List[str]
    :param issue_weights: Relative importance of the issues to the agent. Should be a distribution \
        indexed by issues. Defaults to uniform if none is provided.
    :type issue_weights: Optional[Dict[str, float]]
    :param initial_constraints: A set containing all constraints known to the agent \
        at the beginning defaults to empty if none are given.
    :type initial_constraints: Optional[Set[AtomicConstraint]]
    :param max_rounds: Maximum number of rounds the agent will try to generate an offer. \
        This is to make sure that even impossible negotiations terminate. Defaults to 200
    :type max_rounds: int, optional
    :param auto_constraints: Whether the agent should attempt to automatically deduce \
        whether constraints can be created. ONly works for linear additive utility functions.
        defaults to True
    :type auto_constraints: bool
    :return: The agent with the correct mechanisms initialised.
    :rtype: ConstrainedAgent
    """
    agent = ConstrainedAgent()
    agent.name = name
    agent._type = "Constrained Linear Random"
    agent._neg_space = neg_space
    agent._should_terminate = False

    if not issue_weights:
        issue_weights = {
            issue: 1 / len(neg_space.keys())  for issue in neg_space}

    if not initial_constraints:
        initial_constraints = set()

    if not max_rounds:
        max_rounds = STANDARD_MAX_ROUNDS

    weight_adjusted_utilities = {}
    for atom, util in utilities.items():
        issue, _ = issue_value_tuple_from_atom(atom)
        weight_adjusted_utilities[atom] = util * issue_weights[issue]


    estimate_max_utility = estimate_max_linear_utility(weight_adjusted_utilities)
    reservation_value = reservation_value * estimate_max_utility
    constr_value = -2 * estimate_max_utility
    agent._absolute_reservation_value = reservation_value
    evaluator: Evaluator = ConstrainedLinearEvaluator(
        utilities,
        issue_weights,
        non_agreement_cost,
        constr_value,
        initial_constraints)
    generator: Generator = ConstrainedRandomGenerator(
        neg_space,
        utilities,
        evaluator,
        non_agreement_cost,
        knowledge_base,
        reservation_value,
        max_rounds,
        constr_value,
        initial_constraints,
        auto_constraints=auto_constraints)

    engine: Engine = Engine(generator, evaluator)
    if isclose(reservation_value, 0):
        engine._accepts_all = True
    agent._engine = engine

    return agent
