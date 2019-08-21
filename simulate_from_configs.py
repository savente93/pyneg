import http.client
import multiprocessing as mp
import urllib
from os import remove
from os.path import exists
from uuid import uuid4
from threading import Lock
import pandas as pd
from notify import try_except_notify
from generateScenario import *
from randomNegotiationAgent import RandomNegotiationAgent


def neg_scenario_from_util_matrices(u_a, u_b):
    utils_a = {}
    utils_b = {}
    issues = {}
    number_of_issues_to_generate, issue_cardinality = u_a.shape

    for i in range(number_of_issues_to_generate):
        issues["issue{i}".format(i=i)] = list(range(issue_cardinality))
        for j in range(issue_cardinality):
            if u_a[i, j] != 0:
                utils_a["issue{i}_{j}".format(i=i, j=j)] = u_a[i, j]
            if u_b[i, j] != 0:
                utils_b["issue{i}_{j}".format(i=i, j=j)] = u_b[i, j]

    return issues, utils_a, utils_b


def simulate_negotiation(row_and_index, q):
    _, row = row_and_index
    n, m, rho_a, rho_b, a_accepts, b_accepts, both_accept, p_a, p_b = row.values
    n = int(n)
    m = int(m)
    u_a, u_b = generate_utility_matrices((n, m), 1, 1, kind="lex")
    issues, utils_a, utils_b = neg_scenario_from_util_matrices(u_a, u_b)
    negotiation_id = uuid4()
    non_agreement_cost = -(2 ** 24)  # just a really big number
    agent_a = RandomNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                     issues, name="agent_a")
    agent_b = RandomNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                     issues, name="agent_b")

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


def record_results(q, file):
    from pandas import DataFrame, Series
    counter = 0
    chunksize = 5
    results = DataFrame(columns=["n", "m", "rho_a", "rho_b", "a_accepts", "b_accepts", "both_accept",
                                 "p_a", "p_b"])
    while True:
        m = q.get()
        if m == 'kill':
            break
        counter += 1
        results = results.append(Series(m), ignore_index=True)

        if counter % chunksize == 0:
            results.to_csv(file, index=False)

    results.to_csv(file, index=False)


class ParallelSimulator:
    def __init__(self, results_file, parameter_space, max_queue_size=None, max_pool_size=None):
        self.results_file = results_file
        self.parameter_space = parameter_space
        self.manager = mp.Manager()
        if max_queue_size:
            self.output_queue = self.manager.Queue(maxsize=max_queue_size)
        else:
            self.output_queue = self.manager.Queue()

        if max_pool_size:
            self.work_pool = mp.Pool(max_pool_size)
        else:
            self.work_pool = mp.Pool()

    def shutdown(self):
        print("putting stoptoken in queue")
        self.output_queue.put("kill")
        print("shutting down workers")
        self.work_pool.close()
        self.work_pool.join()

    def start_work(self):
        if exists(self.results_file):
            remove(self.results_file)
        print("Starting recorder")
        # this must be apply_async because it has to work while the rest of the code continues
        self.work_pool.apply_async(
            record_results, (self.output_queue, self.results_file))

        print("Starting workers")
        self.work_pool.starmap(simulate_negotiation, [(
            x, self.output_queue) for x in self.parameter_space])


@try_except_notify
def main():
    result_file = "results.csv"
    config_file = "configs.csv"
    configs = pd.read_csv(config_file, index_col=False)

    param_space = configs.iterrows()
    simulator = ParallelSimulator(result_file, param_space, max_queue_size=15)
    simulator.start_work()
    simulator.shutdown()


main(1)
