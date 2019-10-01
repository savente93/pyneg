import traceback
from os.path import join, abspath

import numpy as np  # type: ignore
from pandas import Series

from pyneg.agent import AgentFactory
from pyneg.types import MessageType
from pyneg.utils import neg_scenario_from_util_matrices


def main():
    config = {'id': '/home/sam/Documents/code/work/pyneg/results/6d71df9c-9682-48bd-8544-da87dcbe8356',
              'constr_count': 0,
              'rho_a': 0.3333333333333333,
              'rho_b': 0.5333333333333333,
              'a_accepts': 7699,
              'b_accepts': 3197,
              'both_accept': 3143,
              'p_a': 0.4082348356929472,
              'p_b': 0.9831091648420394,
              'p_ap_b': 0.4013394083775205,
              'strat': 'Constrained Enumeration'}

    _id, cntr, rho_a, rho_b, a_accepts, b_accepts, both_accept, p_a, p_b, p_ap_b, strat = config.values()
    a = np.load(abspath(join(_id, str(int(cntr)), "a.npy")))
    b = np.load(abspath(join(_id, str(int(cntr)), "b.npy")))
    issues, utils_a, utils_b = neg_scenario_from_util_matrices(a, b)
    non_agreement_cost = -(2 ** 24)  # just a really big number
    try:
        if strat == "Random":

            agent_a = AgentFactory.make_linear_random_agent("A", issues, utils_a, rho_a, non_agreement_cost)
            agent_b = AgentFactory.make_linear_random_agent("B", issues, utils_b, rho_b, non_agreement_cost)
        elif strat == "Enumeration":
            agent_a = AgentFactory.make_linear_concession_agent("A", issues, utils_a, rho_a, non_agreement_cost, None)
            agent_b = AgentFactory.make_linear_concession_agent("B", issues, utils_b, rho_b, non_agreement_cost, None)

        elif strat == "Constrained Random":
            agent_a = AgentFactory.make_constrained_linear_random_agent("A", issues, utils_a, rho_a, non_agreement_cost,
                                                                        [])
            agent_b = AgentFactory.make_constrained_linear_random_agent("B", issues, utils_b, rho_b, non_agreement_cost,
                                                                        [])
        elif strat == "Constrained Enumeration":
            print("starting constrained random simulation")
            agent_a = AgentFactory.make_constrained_linear_concession_agent("A", issues, utils_a, rho_a,
                                                                            non_agreement_cost, None, set())
            agent_b = AgentFactory.make_constrained_linear_concession_agent("B", issues, utils_b, rho_b,
                                                                            non_agreement_cost, None, set())

        else:
            raise ValueError("unknown agent type: {}".format(strat))

        # agent_a.setup_negotiation(issues)
        agent_a.negotiate(agent_b)
    except Exception as e:
        print(
            "following exception was raised during exceution of {}".format(
                config))
        traceback.print_exc()
        raise RuntimeError()

    if agent_a._transcript[-1].type_ == MessageType.ACCEPT:
        util_a = agent_a._engine.calc_offer_utility(agent_a._transcript[-1].offer)
        util_b = agent_b._engine.calc_offer_utility(agent_a._transcript[-1].offer)
    else:
        util_a = non_agreement_cost
        util_b = non_agreement_cost

    print(Series({"id": _id,
                  "constr_count": cntr,
                  "rho_a": rho_a,
                  "rho_b": rho_b,
                  "a_accepts": a_accepts,
                  "b_accepts": b_accepts,
                  "both_accept": both_accept,
                  "p_a": p_a,
                  "p_b": p_b,
                  "p_ap_b": p_ap_b,
                  'success': agent_a.successful,
                  'total_message_count': len(agent_a._transcript),
                  'strat': agent_a._type,
                  'utility': util_a,
                  'opponent_utility': util_b,
                  'transcript': "\n".join(map(str, agent_a._transcript))}))


main()
