import traceback
from functools import partial
from os import path, listdir
from itertools import product

import pandas as pd  # type: ignore

from parallel_simulator import ParallelSimulator, record_results_as_csv
from pyneg.agent import AgentFactory
from pyneg.comms import try_except_notify
from pyneg.types import MessageType
from pyneg.utils import neg_scenario_from_util_matrices, setup_random_scenarios

import numpy as np



def explore_scenarios(row, q):
    from os.path import join, abspath
    from numpy import load, isclose
    from pyneg.utils import count_acceptable_offers
    _id, cntr, rho_a, rho_b, strat = row
    a = load(abspath(join(_id, str(cntr), "a.npy")))
    b = load(abspath(join(_id, str(cntr), "b.npy")))

    a_accepts, b_accepts, both_accept = count_acceptable_offers(
        a, b, rho_a, rho_b)

    p_a = both_accept / a_accepts if a_accepts != 0 else 0
    p_b = both_accept / b_accepts if b_accepts != 0 else 0

    if isclose(rho_a,0) or isclose(rho_b,0):
        p_ap_b = 1.0
    elif isclose(p_a,0) or isclose(p_b,0):
        p_ap_b = 0.0
    else:
        p_ap_b = p_a*p_b

    if p_ap_b <= 0.9:
        q.put({
            "id": _id,
            "constr_count": cntr,
            "rho_a": rho_a,
            "rho_b": rho_b,
            "strat": strat,
            "a_accepts": a_accepts,
            "b_accepts": b_accepts,
            "both_accept": both_accept,
            "p_a": p_a,
            "p_b": p_b,
            "p_ap_b": p_ap_b
        })


def simulate_negotiations(config, q):
    from os.path import join, abspath
    import numpy as np  # type: ignore
    id_, cntr, rho_a, rho_b, a_accepts, b_accepts, both_accept, p_a, p_b, p_ap_b, strat = config.values()
    a = np.load(abspath(join("results", "outliers", id_, "a.npy")))
    b = np.load(abspath(join("results", "outliers", id_, "b.npy")))
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

    q.put({"id": id_,
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
           'transcript': "\n".join(map(str,agent_a._transcript))})

@try_except_notify
def main():
    n_scenarios = 10
    shape = (5, 5)
    rho_sample_rate = 10
    scenario_dir = path.abspath("./results/test/")
    configs_file = path.abspath("./results/test/configs.csv")
    results_file = path.abspath("./results/test/results.csv")
    strats = ["Random", "Enumeration", "Constrained Random", "Constrained Enumeration"]
    setup_random_scenarios(scenario_dir, shape, n_scenarios)
    ids = map(lambda x: path.abspath(
        path.join(scenario_dir, x)), listdir(scenario_dir))
    rho_a_range = np.linspace(0, 1, rho_sample_rate)
    rho_b_range = np.linspace(0, 1, rho_sample_rate)
    csv_columns = ["id", "constr_count", "rho_a", "rho_b",
                   "a_accepts", "b_accepts", "both_accept",
                   "p_a", "p_b", "p_ap_b"]
    record_func = partial(record_results_as_csv, columns=csv_columns)
    param_space = product(
        *[ids,
          range(3*shape[0]),
          rho_a_range,
          rho_b_range,
          strats])

    # First explore the scenarios and calculate the probabilities
    simulator = ParallelSimulator()
    simulator.set_results_file(configs_file)
    simulator.set_parameter_space(param_space)
    simulator.start_work(explore_scenarios, record_func)
    # simulator.shutdown()

    csv_columns = ["id", "constr_count", "rho_a", "rho_b",
                   "a_accepts", "b_accepts", "both_accept",
                   "p_a", "p_b", "p_ap_b",
                   'success',
                   'total_message_count',
                   'strat',
                   'utility',
                   'opponent_utility',
                   'transcript'
                   ]
    record_func = partial(record_results_as_csv, columns=csv_columns)
    simulator.set_results_file(results_file)
    simulator.set_parameter_space(pd.read_csv(
        configs_file).to_dict(orient="index").values())
    simulator.start_work(simulate_negotiations, record_func)
    simulator.shutdown()


main(1)
