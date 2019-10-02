from typing import Dict, Optional, List, Set, Union

from pyneg.agent import Agent, ConstrainedAgent
from pyneg.comms import AtomicConstraint
from pyneg.engine import ConstrainedEnumGenerator
from pyneg.engine import ConstrainedLinearEvaluator
from pyneg.engine import Evaluator, LinearEvaluator, ProblogEvaluator
from pyneg.engine import Generator, EnumGenerator, Engine, RandomGenerator
from pyneg.engine import ConstrainedRandomGenerator
from pyneg.types import NegSpace
from pyneg.utils import nested_dict_from_atom_dict, issue_value_tuple_from_atom
from types import MethodType
from numpy import isclose

STANDARD_MAX_ROUNDS = 200


class AgentFactory:
    @staticmethod
    def estimate_max_linear_utility(utilities: Dict[str, float]) -> float:
        nested_utilities = nested_dict_from_atom_dict(utilities)
        max_utility_by_issue = {issue: -(10.0**10) for issue in nested_utilities.keys()}
        for issue in nested_utilities.keys():
            for value, util in nested_utilities[issue].items():
                if max_utility_by_issue[issue] < util:
                    max_utility_by_issue[issue] = util

        return sum(max_utility_by_issue.values())

    @staticmethod
    def make_linear_concession_agent(name: str,
                                     neg_space: NegSpace,
                                     utilities: Dict[str, float],
                                     reservation_value: float,
                                     non_agreement_cost: float,
                                     issue_weights: Optional[Dict[str, float]]) -> Agent:
        agent = Agent()
        agent.name = name
        agent._type = "Linear Concession"
        agent._neg_space = neg_space

        if not issue_weights:
            issue_weights = {issue: 1 / len(neg_space[issue]) for issue in neg_space.keys()}

        weight_adjusted_utilities = {}
        for atom, util in utilities.items():
            issue, value = issue_value_tuple_from_atom(atom)
            weight_adjusted_utilities[atom] = util * issue_weights[issue]


        estimate_max_utility = AgentFactory.estimate_max_linear_utility(weight_adjusted_utilities)
        reservation_value = reservation_value * estimate_max_utility
        agent._absolute_reservation_value = reservation_value
        evaluator: Evaluator = LinearEvaluator(utilities, issue_weights, non_agreement_cost)
        generator: Generator = EnumGenerator(neg_space, utilities, evaluator, reservation_value)

        engine: Engine = Engine(generator, evaluator)
        if isclose(reservation_value, 0):
            engine._accepts_all = True

        agent._engine = engine

        return agent

    @staticmethod
    def make_linear_random_agent(name: str,
                                 neg_space: NegSpace,
                                 utilities: Dict[str, float],
                                 reservation_value: float,
                                 non_agreement_cost: float,
                                 issue_weights: Optional[Dict[str, float]] = None,
                                 max_rounds: int = None) -> Agent:

        agent = Agent()
        agent.name = name
        agent._type = "Linear Random"
        agent._neg_space = neg_space

        if not issue_weights:
            issue_weights = {issue: 1 / len(neg_space[issue]) for issue in neg_space.keys()}

        if not max_rounds:
            max_rounds = STANDARD_MAX_ROUNDS

        weight_adjusted_utilities = {}
        for atom, util in utilities.items():
            issue, value = issue_value_tuple_from_atom(atom)
            weight_adjusted_utilities[atom] = util * issue_weights[issue]

        estimate_max_utility = AgentFactory.estimate_max_linear_utility(weight_adjusted_utilities)
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

    @staticmethod
    def make_random_agent(name: str,
                          neg_space: NegSpace,
                          utilities: Dict[str, float],
                          reservation_value: Union[float, int],
                          non_agreement_cost: float,
                          kb: List[str],
                          max_rounds: int = None) -> Agent:

        agent = Agent()
        agent.name = name
        agent._type = "Random"
        agent._neg_space = neg_space

        if not max_rounds:
            max_rounds = STANDARD_MAX_ROUNDS


        estimate_max_utility = AgentFactory.estimate_max_linear_utility(utilities)
        reservation_value = reservation_value * estimate_max_utility

        agent._absolute_reservation_value = reservation_value
        evaluator: Evaluator = ProblogEvaluator(neg_space,
                                                utilities, non_agreement_cost, kb)
        generator: Generator = RandomGenerator(
            neg_space, utilities, evaluator, reservation_value, [], reservation_value,max_rounds)

        engine = Engine(generator, evaluator)
        if isclose(reservation_value, 0):
            engine._accepts_all = True
        agent._engine = engine

        return agent

    @staticmethod
    def make_constrained_linear_concession_agent(name: str,
                                                 neg_space: NegSpace,
                                                 utilities: Dict[str, float],
                                                 reservation_value: float,
                                                 non_agreement_cost: float,
                                                 issue_weights: Optional[Dict[str, float]],
                                                 initial_constraints: Optional[Set[AtomicConstraint]],
                                                 auto_constraints=True) -> ConstrainedAgent:
        agent = ConstrainedAgent()
        agent.name = name
        agent._type = "Constrained Linear Concession"
        agent._neg_space = neg_space

        if not issue_weights:
            issue_weights = {
                issue: 1 / len(neg_space[issue])
                for issue in neg_space.keys()}

        if not initial_constraints:
            initial_constraints = set()

        weight_adjusted_utilities = {}
        for atom, util in utilities.items():
            issue, value = issue_value_tuple_from_atom(atom)
            weight_adjusted_utilities[atom] = util * issue_weights[issue]

        estimate_max_utility = AgentFactory.estimate_max_linear_utility(weight_adjusted_utilities)
        reservation_value = reservation_value * estimate_max_utility
        constr_value = -2 * estimate_max_utility
        agent._absolute_reservation_value = reservation_value
        evaluator: Evaluator = ConstrainedLinearEvaluator(
            utilities, issue_weights, non_agreement_cost, constr_value, initial_constraints)
        generator: Generator = ConstrainedEnumGenerator(
            neg_space, utilities, evaluator, reservation_value,
            constr_value, initial_constraints, auto_constraints=auto_constraints)

        engine: Engine = Engine(generator, evaluator)
        if isclose(reservation_value, 0):
            engine._accepts_all = True
        agent._engine = engine

        return agent

    @staticmethod
    def make_constrained_linear_random_agent(name: str,
                                             neg_space: NegSpace,
                                             utilities: Dict[str, float],
                                             reservation_value: float,
                                             non_agreement_cost: float,
                                             kb: List[str],
                                             issue_weights: Optional[Dict[str, float]] = None,
                                             initial_constraints: Optional[Set[AtomicConstraint]] = None,
                                             max_rounds: int = None,
                                             auto_constraints=True) -> ConstrainedAgent:
        agent = ConstrainedAgent()
        agent.name = name
        agent._type = "Constrained Linear Random"
        agent._neg_space = neg_space

        if not issue_weights:
            issue_weights = {
                issue: 1 / len(neg_space[issue])
                for issue in neg_space.keys()}

        if not initial_constraints:
            initial_constraints = set()

        if not max_rounds:
            max_rounds = STANDARD_MAX_ROUNDS

        weight_adjusted_utilities = {}
        for atom, util in utilities.items():
            issue, _ = issue_value_tuple_from_atom(atom)
            weight_adjusted_utilities[atom] = util * issue_weights[issue]


        estimate_max_utility = AgentFactory.estimate_max_linear_utility(weight_adjusted_utilities)
        reservation_value = reservation_value * estimate_max_utility
        constr_value = -2 * estimate_max_utility
        agent._absolute_reservation_value = reservation_value
        evaluator: Evaluator = ConstrainedLinearEvaluator(
            utilities, issue_weights, non_agreement_cost, constr_value, initial_constraints)
        generator: Generator = ConstrainedRandomGenerator(
            neg_space, utilities, evaluator, non_agreement_cost, kb, reservation_value,
            max_rounds, constr_value, initial_constraints, auto_constraints=auto_constraints)

        engine: Engine = Engine(generator, evaluator)
        if isclose(reservation_value, 0):
            engine._accepts_all = True
        agent._engine = engine

        return agent

