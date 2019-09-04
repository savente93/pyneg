from typing import Dict, Optional, Union, List, Set

from pyneg.agent import Agent, ConstrainedAgent
from pyneg.comms import AtomicConstraint
from pyneg.engine import ConstrainedEnumGenerator
from pyneg.engine import ConstrainedLinearEvaluator
from pyneg.engine import Evaluator, LinearEvaluator, ProblogEvaluator
from pyneg.engine import Generator, EnumGenerator, Engine, RandomGenerator
from pyneg.types import NegSpace
from pyneg.utils import atom_dict_from_nested_dict

STANDARD_MAX_ROUNDS = 200


class AgentFactory():
    @staticmethod
    def make_linear_consession_agent(name: str,
                                     neg_space: NegSpace,
                                     utilities: Union[Dict[str, float],
                                                      Dict[str, Dict[str, float]]],
                                     reservation_value: float,
                                     non_agreement_cost: float,
                                     issue_weights: Optional[Dict[str, float]],
                                     max_rounds: int = None) -> Agent:
        agent = Agent()
        agent.name = name
        agent._type = "Linear Consession"
        if not max_rounds:
            agent.max_rounds = STANDARD_MAX_ROUNDS
        else:
            agent.max_rounds = max_rounds

        if not issue_weights:
            issue_weights = {
                issue: 1 / len(neg_space[issue])
                for issue in neg_space.keys()}

        # convert to atomic dict if we are given a nested dict
        if isinstance(next(iter(utilities.values())), dict):
            utilities = atom_dict_from_nested_dict(utilities)

        evaluator: Evaluator = LinearEvaluator(
            utilities, issue_weights, non_agreement_cost)
        generator: Generator = EnumGenerator(
            neg_space, utilities, evaluator, reservation_value)

        engine: Engine = Engine(generator, evaluator)
        agent.engine = engine
        agent.absolute_reservation_value = generator.acceptability_threshold

        return agent

    @staticmethod
    def make_linear_random_agent(name: str,
                                 neg_space: NegSpace,
                                 utilities: Union[Dict[str, float],
                                                  Dict[str, Dict[str, float]]],
                                 reservation_value: float,
                                 non_agreement_cost: float,
                                 issue_weights: Optional[Dict[str, float]] = None,
                                 max_rounds: int = None) -> Agent:

        agent = Agent()
        agent.name = name
        agent._type = "Linear Random"
        if not max_rounds:
            agent.max_rounds = STANDARD_MAX_ROUNDS
        else:
            agent.max_rounds = max_rounds

        if not issue_weights:
            issue_weights = {
                issue: 1 / len(neg_space[issue])
                for issue in neg_space.keys()}

        # convert to atomic dict if we are given a nested dict
        if isinstance(next(iter(utilities.values())), dict):
            utilities = atom_dict_from_nested_dict(utilities)

        evaluator: Evaluator = LinearEvaluator(
            utilities, issue_weights, non_agreement_cost)
        generator: Generator = RandomGenerator(
            neg_space, utilities, evaluator, reservation_value, [], reservation_value)

        engine = Engine(generator, evaluator)
        agent.engine = engine
        agent.absolute_reservation_value = generator.acceptability_threshold

        return agent

    @staticmethod
    def make_random_agent(name: str,
                          neg_space: NegSpace,
                          utilities: Union[Dict[str, float],
                                           Dict[str, Dict[str, float]]],
                          reservation_value: float,
                          non_agreement_cost: float,
                          kb: List[str],
                          max_rounds: int = None) -> Agent:

        agent = Agent()
        agent.name = name
        agent._type = "Random"
        if not max_rounds:
            agent.max_rounds = STANDARD_MAX_ROUNDS
        else:
            agent.max_rounds = max_rounds

        # convert to atomic dict if we are given a nested dict
        if isinstance(next(iter(utilities.values())), dict):
            utilities = atom_dict_from_nested_dict(utilities)

        evaluator: Evaluator = ProblogEvaluator(neg_space,
                                                utilities, non_agreement_cost, kb)
        generator: Generator = RandomGenerator(
            neg_space, utilities, evaluator, reservation_value, [], reservation_value)

        engine = Engine(generator, evaluator)
        agent.engine = engine
        agent.absolute_reservation_value = generator.acceptability_threshold

        return agent

    @staticmethod
    def make_constrained_linear_consession_agent(name: str,
                                                 neg_space: NegSpace,
                                                 utilities: Union[Dict[str, float],
                                                                  Dict[str, Dict[str, float]]],
                                                 reservation_value: float,
                                                 non_agreement_cost: float,
                                                 issue_weights: Optional[Dict[str, float]],
                                                 initial_constraints: Optional[Set[AtomicConstraint]],
                                                 auto_constraints=True) -> ConstrainedAgent:
        agent = ConstrainedAgent()
        agent.name = name
        agent._type = "Constrained Linear Consession"

        if not issue_weights:
            issue_weights = {
                issue: 1 / len(neg_space[issue])
                for issue in neg_space.keys()}

        # convert to atomic dict if we are given a nested dict
        if isinstance(next(iter(utilities.values())), dict):
            utilities = atom_dict_from_nested_dict(utilities)

        evaluator: Evaluator = ConstrainedLinearEvaluator(
            utilities, issue_weights, non_agreement_cost, initial_constraints)
        generator: Generator = ConstrainedEnumGenerator(
            neg_space, utilities, evaluator, reservation_value, initial_constraints, auto_constraints=auto_constraints)

        engine: Engine = Engine(generator, evaluator)
        agent.engine = engine
        agent.absolute_reservation_value = generator.acceptability_threshold

        return agent
