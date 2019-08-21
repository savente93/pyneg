import multiprocessing as mp
from os import remove
from os.path import exists
import pandas as pd
from generateScenario import *
from notify import try_except_notify


def do_work(args, q):
    n, m, rho_a, rho_b = args
    u_a, u_b = generate_utility_matrices((n, m), 0, 0, kind="lex")
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
        self.work_pool.starmap(
            do_work, [(x, self.output_queue) for x in self.parameter_space])


@try_except_notify
def main():
    n = 5
    m = 5
    result_file = "configs.csv"
    rho_a_range = np.linspace(0, 1, 32)
    rho_b_range = np.linspace(0, 1, 32)

    param_space = product(
        *[[n], [m], rho_a_range, rho_b_range])
    simulator = ParallelSimulator(result_file, param_space)
    simulator.start_work()
    simulator.shutdown()

    # numb_of_bins = 20
    # results = pd.read_csv(result_file, index_col=False)
    # bin_index = pd.IntervalIndex(
    #     pd.cut(results['p_a'], bins=numb_of_bins)).sort_values().unique()
    # results['bin_a'] = pd.cut(results['p_a'], bins=bin_index)
    # results['asym_difficulty'] = results['p_a'] - results['p_b']
    # # [(np.abs(results['asym_difficulty']) < 0.5)] # & (results['p_a'] > 0.01) & (results['p_a'] < 0.95)]
    # admissible_configs = results
    # admissible_configs.to_csv("admissible_configs.csv", index=False)


main(1)
