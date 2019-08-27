from utils import neg_scenario_from_util_matrices, count_acceptable_offers
from rand_agent import Verbosity
import numpy as np
from os.path import join, abspath
from constr_enum_agent import EnumConstrAgent
from message import Message

config = {'id': '/home/sam/Documents/code/work/pyneg/src/scenarios/38fc668f-ecb3-41d3-8e64-c4eab50eef59', 'constr_count': 7, 'rho_a': 1.0,
          'rho_b': 1.0, 'a_accepts': 3, 'b_accepts': 3, 'both_accept': 0, 'p_a': 0.0, 'p_b': 0.0, 'p_ap_b': 0.0, 'strat': 'constr_enum'}

_id, cntr, rho_a, rho_b, a_accepts, b_accepts, both_accept, p_a, p_b, p_ap_b, strat = config.values()
a = np.load(abspath(join(_id, str(cntr), "a.npy")))
b = np.load(abspath(join(_id, str(cntr), "b.npy")))
issues, utils_a, utils_b = neg_scenario_from_util_matrices(a, b)
non_agreement_cost = -(2 ** 24)  # just a really big number

string = '''
        utils_a = {}
        utils_b = {}
        issues = {}
        rho_a = {}
        rho_b = {}

        non_agreement_cost = -(2 ** 24)  # just a really big number

        agent_a = EnumConstrAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                                  issues)
        agent_b = EnumConstrAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                                  issues)

        self.assertTrue(agent_a.negotiate(agent_b))'''.format(utils_a, utils_b, issues, rho_a, rho_b)

print(string)
# agent_a = EnumConstrAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
#                           issues, verbose=Verbosity.debug)
# agent_b = EnumConstrAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
#                           issues)
# agent_a.negotiate(agent_b)
