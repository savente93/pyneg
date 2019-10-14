import traceback
from functools import partial
from os import path, listdir, remove
from itertools import product, starmap

import pandas as pd  # type: ignore

from tqdm import tqdm
import ray
from pandas import Series
from parallel_simulator import ParallelSimulator, record_results_as_csv
from pyneg.agent import AgentFactory
from pyneg.comms import send_message
from pyneg.types import MessageType
from pyneg.utils import neg_scenario_from_util_matrices, setup_random_scenarios

from os import walk,remove,path, rmdir
import numpy as np


@ray.remote
def explore_scenarios(row):
    from os.path import join, abspath
    from numpy import load,isclose
    from pyneg.utils import count_acceptable_offers

    _id, cntr, rho_a, rho_b, strat = row

    if isclose(rho_a*rho_b,0):
        return {}

    a = load(abspath(join("./sims/scenarios",_id, str(cntr), "a.npy")))
    b = load(abspath(join("./sims/scenarios",_id, str(cntr), "b.npy")))

    a_accepts, b_accepts, both_accept = count_acceptable_offers(
        a, b, rho_a, rho_b)

    p_a = both_accept / a_accepts if a_accepts != 0 else 0
    p_b = both_accept / b_accepts if b_accepts != 0 else 0
    p_ap_b = p_a*p_b

    return {
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
        }

if __name__ == "__main__":
    ray.init()
    n_scenarios = 15
    shape = (7, 8)
    rho_sample_rate = 20
    numb_of_constraints = 24
    scenario_dir = path.abspath("./sims/scenarios/")
    configs_file = path.abspath("./sims/results/configs.csv")
    results_file = path.abspath("./sims/results/results.csv")

    if path.exists(configs_file):
        remove(configs_file)

    if path.exists(results_file):
        remove(results_file)

    for root, dirs, files in walk(scenario_dir, topdown=False):
        for name in files:
            remove(path.join(root, name))
        for name in dirs:
          rmdir(path.join(root, name))

    strats = reversed(["Random", "Enumeration", "Constrained Random", "Constrained Enumeration"])
    setup_random_scenarios(scenario_dir, shape, n_scenarios,numb_of_constraints)
    ids = map(lambda x: path.abspath(
        path.join(scenario_dir, x)), listdir(scenario_dir))
    rho_a_range = np.linspace(0.1, 1, rho_sample_rate)
    rho_b_range = np.linspace(0.1, 1, rho_sample_rate)
    csv_columns = ["id", "constr_count", "rho_a", "rho_b",
                   "a_accepts", "b_accepts", "both_accept",
                   "p_a", "p_b", "p_ap_b"]

    record_func = partial(record_results_as_csv, columns=csv_columns)
    param_space = product(
        *[ids,
          range(numb_of_constraints),
          rho_a_range,
          rho_b_range,
          strats])

    remaining = [explore_scenarios.remote(config) for config in param_space]
    t = tqdm(total=len(remaining))
    finished, remaining = ray.wait(remaining, num_returns=1)
    with open(configs_file, "a") as f:
        f.write(pd.DataFrame(ray.get(finished)).to_csv(header=True, index=False))

    while len(remaining) > 0:
        finished, remaining = ray.wait(remaining,num_returns=min(20,len(remaining)))
        t.update(len(finished))

        with open(configs_file,"a") as f:
            f.write(pd.DataFrame(ray.get(finished)).to_csv(header=False,index=False))

    with open(configs_file,"a") as f:
        f.write(pd.DataFrame(ray.get(finished)).to_csv(header=False,index=False))

    send_message("Scenario generation is done")
