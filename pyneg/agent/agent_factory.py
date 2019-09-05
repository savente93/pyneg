from typing import Dict, Optional, List, Set, Union

from pyneg.agent import Agent, ConstrainedAgent
from pyneg.comms import AtomicConstraint
from pyneg.engine import ConstrainedEnumGenerator
from pyneg.engine import ConstrainedLinearEvaluator
from pyneg.engine import Evaluator, LinearEvaluator, ProblogEvaluator
from pyneg.engine import Generator, EnumGenerator, Engine, RandomGenerator
from pyneg.types import NegSpace
from pyneg.utils import nested_dict_from_atom_dict
STANDARD_MAX_ROUNDS = 200


class AgentFactory:
    @staticmethod
    def estimate_max_utility(utilities: Dict[str, float]) -> float:
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
                                     reservation_value: Union[float, int],
                                     non_agreement_cost: float,
                                     issue_weights: Optional[Dict[str, float]]) -> Agent:
        agent = Agent()
        agent.name = name
        agent._type = "Linear Concession"

        if not issue_weights:
            issue_weights = {issue: 1 / len(neg_space[issue]) for issue in neg_space.keys()}

        if isinstance(reservation_value, float):
            estimate_max_utility = AgentFactory.estimate_max_utility(utilities)
            reservation_value = reservation_value * estimate_max_utility

        evaluator: Evaluator = LinearEvaluator(utilities, issue_weights, non_agreement_cost)
        generator: Generator = EnumGenerator(neg_space, utilities, evaluator, reservation_value)

        engine: Engine = Engine(generator, evaluator)
        agent._engine = engine
        return agent

    @staticmethod
    def make_linear_random_agent(name: str,
                                 neg_space: NegSpace,
                                 utilities: Dict[str, float],
                                 reservation_value: Union[float, int],
                                 non_agreement_cost: float,
                                 issue_weights: Optional[Dict[str, float]] = None,
                                 max_rounds: int = None) -> Agent:

        agent = Agent()
        agent.name = name
        agent._type = "Linear Random"
        if not max_rounds:
            agent._max_rounds = STANDARD_MAX_ROUNDS
        else:
            agent._max_rounds = max_rounds

        if not issue_weights:
            issue_weights = {issue: 1 / len(neg_space[issue]) for issue in neg_space.keys()}

        if isinstance(reservation_value, float):
            estimate_max_utility = AgentFactory.estimate_max_utility(utilities)
            reservation_value = reservation_value * estimate_max_utility

        evaluator: Evaluator = LinearEvaluator(utilities, issue_weights, non_agreement_cost)
        generator: Generator = RandomGenerator(
            neg_space,
            utilities,
            evaluator,
            non_agreement_cost, [],
            reservation_value)

        engine = Engine(generator, evaluator)
        agent._engine = engine

        return agent

    @staticmethod
    def make_constrained_linear_concession_agent(name: str,
                                                 neg_space: NegSpace,
                                                 utilities: Dict[str, float],
                                                 reservation_value: Union[float, int],
                                                 non_agreement_cost: float,
                                                 issue_weights: Optional[Dict[str, float]],
                                                 initial_constraints: Optional[Set[AtomicConstraint]],
                                                 auto_constraints=True) -> ConstrainedAgent:
        agent = ConstrainedAgent()
        agent.name = name
        agent._type = "Constrained Linear Concession"

        if not issue_weights:
            issue_weights = {
                issue: 1 / len(neg_space[issue])
                for issue in neg_space.keys()}

        if isinstance(reservation_value, float):
            estimate_max_utility = AgentFactory.estimate_max_utility(utilities)
            reservation_value = reservation_value * estimate_max_utility

        evaluator: Evaluator = ConstrainedLinearEvaluator(
            utilities, issue_weights, non_agreement_cost, initial_constraints)
        generator: Generator = ConstrainedEnumGenerator(
            neg_space, utilities, evaluator, reservation_value, initial_constraints, auto_constraints=auto_constraints)

        engine: Engine = Engine(generator, evaluator)
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
        if not max_rounds:
            agent._max_rounds = STANDARD_MAX_ROUNDS
        else:
            agent._max_rounds = max_rounds

        if isinstance(reservation_value, float):
            estimate_max_utility = AgentFactory.estimate_max_utility(utilities)
            reservation_value = reservation_value * estimate_max_utility

        evaluator: Evaluator = ProblogEvaluator(neg_space,
                                                utilities, non_agreement_cost, kb)
        generator: Generator = RandomGenerator(
            neg_space, utilities, evaluator, reservation_value, [], reservation_value)

        engine = Engine(generator, evaluator)
        agent._engine = engine

        return agent