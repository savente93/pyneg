from utils import neg_scenario_from_util_matrices, count_acceptable_offers, setup_random_scenarios
from rand_agent import RandAgent, Verbosity
from constr_agent import ConstrAgent
from enum_agent import EnumAgent
from constr_enum_agent import EnumConstrAgent
from parallel_simulator import ParallelSimulator, record_results_as_csv
from notify import try_except_notify
from functools import partial
from itertools import product
import numpy as np
from os import listdir, path
import pandas as pd
import traceback


def explore_scenarios(row, q):
    from os.path import join, abspath
    import numpy as np
    _id, cntr, rho_a, rho_b, strat = row
    a = np.load(abspath(join(_id, str(cntr), "a.npy")))
    b = np.load(abspath(join(_id, str(cntr), "b.npy")))

    a_accepts, b_accepts, both_accept = count_acceptable_offers(
        a, b, rho_a, rho_b)

    p_a = both_accept / a_accepts if a_accepts != 0 else 0
    p_b = both_accept / b_accepts if b_accepts != 0 else 0

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
        "p_ap_b": p_a * p_b
    })


def simulate_negotiations(config, q):
    from os.path import join, abspath
    import numpy as np
    # print(config)
    _id, cntr, rho_a, rho_b, a_accepts, b_accepts, both_accept, p_a, p_b, p_ap_b, strat = config.values()
    a = np.load(abspath(join(_id, str(cntr), "a.npy")))
    b = np.load(abspath(join(_id, str(cntr), "b.npy")))
    issues, utils_a, utils_b = neg_scenario_from_util_matrices(a, b)
    non_agreement_cost = -(2 ** 24)  # just a really big number
    try:
        if strat == "rand":
            agent_a = RandAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                                issues)
            agent_b = RandAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                                issues)
        elif strat == "enum":
            agent_a = EnumAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                                issues)
            agent_b = EnumAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                                issues)
        elif strat == "constr_rand":
            agent_a = ConstrAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                                  issues)
            agent_b = ConstrAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                                  issues)
        elif strat == "constr_enum":

            agent_a = EnumConstrAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                                      issues)
            agent_b = EnumConstrAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                                      issues)

        else:
            raise ValueError("unknown agent type: {}".format(strat))

        agent_a.setup_negotiation(issues)
        agent_a.negotiate(agent_b)
    except Exception as e:
        print(
            "following exception was raised during exceution of {}".format(
                config))
        traceback.print_exc()
        raise RuntimeError()

    if len(agent_a.transcript) > 0:
        util_a = agent_a.calc_offer_utility(agent_a.transcript[-1].offer)
        util_b = agent_b.calc_offer_utility(agent_a.transcript[-1].offer)
    else:
        util_a = non_agreement_cost
        util_b = non_agreement_cost
    q.put({"id": _id,
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
           'total_message_count': len(agent_a.transcript),
           'n_constraints': cntr,
           'n_constraints_discovered': len(agent_a.opponent_constraints),
           'n_constraints_opponent_discovered': len(agent_b.opponent_constraints),
           'strat': agent_a.strat_name,
           'opponent_strat': agent_b.strat_name,
           'utility': util_a,
           'opponent_utility': util_b})


@try_except_notify
def main():
    n_scenarios = 10
    shape = (8, 7)
    rho_sample_rate = 10
    scenario_dir = path.abspath("./src/scenarios")
    configs_file = path.abspath("./results/rand_configs.csv")
    results_file = path.abspath("./results/rand_results.csv")
    strats = ["rand", "enum", "constr_rand", "constr_enum"]
    setup_random_scenarios(scenario_dir, shape, n_scenarios)
    ids = map(lambda x: path.abspath(
        path.join(scenario_dir, x)), listdir(scenario_dir))
    # ids = ["/home/sam/Documents/code/work/pyneg/src/scenarios/90324efb-7f51-4552-ab9c-e882f255f0b3"]
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
    simulator.shutdown()

    # Actually simmulate the negotiations
    csv_columns = ["id", "constr_count", "rho_a", "rho_b",
                   "a_accepts", "b_accepts", "both_accept",
                   "p_a", "p_b", "p_ap_b",
                   'success', 'total_message_count', 'n_constraints',
                   'n_constraints_discovered', 'n_constraints_opponent_discovered',
                   'strat', 'utility', 'opponent_utility'
                   ]
    record_func = partial(record_results_as_csv, columns=csv_columns)
    simulator.set_results_file(results_file)
    simulator.set_parameter_space(pd.read_csv(
        configs_file).to_dict(orient="index").values())
    simulator.start_work(simulate_negotiations, record_func)
    simulator.shutdown()


main(1)
