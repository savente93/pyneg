from typing import Dict, Optional, Union, List
from pyneg.engine import Evaluator, LinearEvaluator, ProblogEvaluator, DTPGenerator, Generator, EnumGenerator, Engine, RandomGenerator
from pyneg.utils import atom_dict_from_nested_dict
from pyneg.agent import Agent
from pyneg.types import NegSpace


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
                issue: 1/len(neg_space[issue])
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
                issue: 1/len(neg_space[issue])
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
