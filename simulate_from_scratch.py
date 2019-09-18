import numpy as np
import pandas as pd
from itertools import product
from functools import partial
from notify import try_except_notify
from parallel_simulator import ParallelSimulator, record_results_as_csv
from utils import generate_lex_utility_matrices, count_acceptable_offers, neg_scenario_from_util_matrices


def generate_lex_scenarios(args, q):
    n, m, rho_a, rho_b = args
    u_a, u_b = generate_lex_utility_matrices((n, m), 3)
    a, b, both = count_acceptable_offers(u_a, u_b, rho_a, rho_b)
    q.put({"n": n,
           "m": m,
           "rho_a": rho_a,
           "rho_b": rho_b,
           "a_accepts": a,
           "b_accepts": b,
           "both_accept": both,
           "p_a": both / a if a != 0 else 0,
           "p_b": both / b if b != 0 else 0})


def simulate_random_negotiation(row_and_index, q):
    _, row = row_and_index
    n, m, rho_a, rho_b, a_accepts, b_accepts, both_accept, p_a, p_b = row.values
    n = int(n)
    m = int(m)
    u_a, u_b = generate_lex_utility_matrices((n, m), 3)
    issues, utils_a, utils_b = neg_scenario_from_util_matrices(u_a, u_b)
    non_agreement_cost = -(2 ** 24)  # just a really big number
    agent_a = RandAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                        issues)
    agent_b = RandAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                        issues)

    agent_a.setup_negotiation(issues)
    agent_a.negotiate(agent_b)

    q.put({"n": n,
           "m": m,
           "rho_a": rho_a,
           "rho_b": rho_b,
           "a_accepts": a_accepts,
           "b_accepts": b_accepts,
           "both_accept": both_accept,
           "p_a": p_a,
           "p_b": p_b,
           'success': agent_a.successful,
           'total_message_count': agent_a.message_count + agent_b.message_count,
           'numb_of_own_constraints': 0,
           'numb_of_discovered_constraints': 0,
           'numb_of_opponent_constraints': 0,
           'strat': agent_a.strat_name,
           'opponent_strat': agent_b.strat_name,
           'utility': agent_a.calc_offer_utility(agent_a.transcript[-1].offer),
           'opponent_utility': agent_b.calc_offer_utility(agent_b.transcript[-1].offer),
           'total_generated_offers': agent_a.total_offers_generated + agent_b.total_offers_generated
           })


@try_except_notify
def main():
    result_dir = "results"
    configs_file = "{result_dir}/configs.csv".format(result_dir=result_dir)
    result_file = "{result_dir}/results.csv".format(
        result_dir=result_dir)
    n = 5
    m = 5
    rho_sample_rate = 32
    rho_a_range = np.linspace(0, 1, rho_sample_rate)
    rho_b_range = np.linspace(0, 1, rho_sample_rate)
    csv_columns = []
    record_func = partial(record_results_as_csv, columns=csv_columns)
    param_space = product(*[[n], [m], rho_a_range, rho_b_range])

    # First generate the scenarios
    simulator = ParallelSimulator()
    simulator.set_results_file(configs_file)
    simulator.set_parameter_space(param_space)
    simulator.start_work(generate_lex_scenarios, record_func)
    simulator.shutdown()

    # Actually simmulate the negotiations
    csv_columns = ["n", "m", "rho_a", "rho_b", "a_accepts", "b_accepts", "both_accept",
                        "p_a", "p_b", 'success', 'total_message_count',
                        'numb_of_own_constraints', 'numb_of_discovered_constraints',
                        'numb_of_opponent_constraints', 'strat', 'opponent_strat',
                        'utility', 'opponent_utility', 'total_generated_offers']
    record_func = partial(record_results_as_csv, columns=csv_columns)
    simulator.set_results_file(result_file)
    simulator.set_parameter_space(param_space)
    simulator.start_work(simulate_random_negotiation, record_func)
    simulator.shutdown()


main()
