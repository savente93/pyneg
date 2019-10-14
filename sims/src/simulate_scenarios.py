import traceback
from os import path
from tqdm import tqdm
import pandas as pd  # type: ignore
import ray
from pyneg.agent import AgentFactory
from pyneg.comms import send_message
from pyneg.types import MessageType
from pyneg.utils import neg_scenario_from_util_matrices

@ray.remote
def simulate_negotiations(config):
    from os.path import join, abspath
    import numpy as np  # type: ignore
    _id, cntr, rho_a, rho_b,strat, a_accepts, b_accepts, both_accept, p_a, p_b, p_ap_b = config.values
    a = np.load(abspath(join("./sims/scenarios",_id, str(cntr), "a.npy")))
    b = np.load(abspath(join("./sims/scenarios",_id, str(cntr), "b.npy")))
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
            return {}
            #agent_a = AgentFactory.make_constrained_linear_concession_agent("A", issues, utils_a, rho_a,
            #                                                                non_agreement_cost, set(), None)
            #agent_b = AgentFactory.make_constrained_linear_concession_agent("B", issues, utils_b, rho_b,
            #                                                                non_agreement_cost, set(), None)

        else:
            raise ValueError("unknown agent type: {}".format(strat))

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

    return{"id": _id,
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
           'transcript': "\n".join(map(str,agent_a._transcript))}


if __name__ == "__main__":
    try:
        print("ray init...")
        ray.init()
        configs_file = path.abspath("./sims/results/configs.csv")
        results_file = path.abspath("./sims/results/results.csv")
        param_space = [config for _,config in pd.read_csv(configs_file).iterrows()]

        remaining = [simulate_negotiations.remote(config) for config in param_space]
        t = tqdm(total=len(remaining))
        finished, remaining = ray.wait(remaining, num_returns=1)
        with open(results_file, "a") as f:
             f.write(pd.DataFrame(ray.get(finished)).to_csv(header=True,index=False))

        print("work has started")
        while len(remaining) > 0:
            finished, remaining = ray.wait(remaining, num_returns=min(20,len(remaining)))
            t.update(len(finished))

            with open(results_file, "a") as f:
                f.write(pd.DataFrame(ray.get(finished)).to_csv(header=False, index=False))


        send_message("simulations are done")
    except:
        send_message("simulations crached")
