import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from randomNegotiationAgent import RandomNegotiationAgent, Verbosity
from constraintNegotiationAgent import ConstraintNegotiationAgent
from generateScenario import *
from uuid import uuid4


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



n = 6
m = 6
tau_a = 4
tau_b = 4
rho_a = 0.5
rho_b = 0.5
constr_val = -1000
negotiation_id = uuid4()
non_agreement_cost = -(2 ** 24)
base_case_a, base_case_b = generate_utility_matrices((n, m), tau_a, tau_b)
a,b,both = count_acceptable_offers(base_case_a, base_case_b, rho_a, rho_b)
p_a = both/a if a!=0 else 0
print("a: {}, b:{}, both: {}, p_a:{}".format(a,b,both,p_a))
if p_a<0.001 or p_a > 0.6:
    exit()
results = pd.DataFrame(
    columns=['scenario', 'strat', 'success', 'total_message_count'])


issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    base_case_a, base_case_b)
agent_a = RandomNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                 issues, name="agent_a")
agent_b = RandomNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                 issues, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "base",
                          'strat': "random",
                          'success': agent_a.successful,
                          'total_message_count': agent_a.message_count + agent_b.message_count}, ignore_index=True)

issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    base_case_a, base_case_b)
agent_a = ConstraintNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                 issues,  max_rounds=500, name="agent_a")
agent_b = ConstraintNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                 issues,  max_rounds=500, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "base",
                          'strat': "constraint",
                          'success': agent_a.successful,
                          'total_message_count': len(agent_a.transcript)}, ignore_index=True)
print(agent_a.transcript)
print("base case done")


single_constrained_a = base_case_a.copy()
single_constrained_b = base_case_b.copy()
single_constrained_a[0, 0] = constr_val

issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    single_constrained_a, single_constrained_b)
agent_a = RandomNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                 issues, name="agent_a")
agent_b = RandomNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                 issues, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "single",
                          'strat': "random",
                          'success': agent_a.successful,
                          'total_message_count': agent_a.message_count + agent_b.message_count}, ignore_index=True)

issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    single_constrained_a, single_constrained_b)
agent_a = ConstraintNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                     issues, name="agent_a")
agent_b = ConstraintNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                     issues, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "single",
                          'strat': "constraint",
                          'success': agent_a.successful,
                          'total_message_count': agent_a.message_count + agent_b.message_count}, ignore_index=True)
print("single constraint case done")


col_constrained_a = base_case_a.copy()
col_constrained_b = base_case_b.copy()
col_constrained_a[:, 0] = constr_val

issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    col_constrained_a, col_constrained_b)
agent_a = RandomNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                 issues, name="agent_a")
agent_b = RandomNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                 issues, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "col",
                          'strat': "random",
                          'success': agent_a.successful,
                          'total_message_count': agent_a.message_count + agent_b.message_count}, ignore_index=True)

issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    col_constrained_a, col_constrained_b)
agent_a = ConstraintNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                     issues, name="agent_a")
agent_b = ConstraintNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                     issues, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "col",
                          'strat': "constraint",
                          'success': agent_a.successful,
                          'total_message_count': agent_a.message_count + agent_b.message_count}, ignore_index=True)
print("col constraint case done")

row_constrained_a = base_case_a.copy()
row_constrained_b = base_case_b.copy()
row_constrained_a[1, :3] = constr_val
row_constrained_b[1, 3:] = constr_val

issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    row_constrained_a, row_constrained_b)
agent_a = RandomNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                 issues, name="agent_a")
agent_b = RandomNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                 issues, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "row",
                          'strat': "random",
                          'success': agent_a.successful,
                          'total_message_count': agent_a.message_count + agent_b.message_count}, ignore_index=True)


issues, utils_a, utils_b = neg_scenario_from_util_matrices(
    row_constrained_a, row_constrained_b)
agent_a = ConstraintNegotiationAgent(negotiation_id, utils_a, [], rho_a, non_agreement_cost,
                                     issues, name="agent_a")
agent_b = ConstraintNegotiationAgent(negotiation_id, utils_b, [], rho_b, non_agreement_cost,
                                     issues, name="agent_b")
agent_a.setup_negotiation(issues)
agent_a.negotiate(agent_b)
results = results.append({'scenario': "row",
                          'strat': "constraint",
                          'success': agent_a.successful,
                          'total_message_count': agent_a.message_count + agent_b.message_count}, ignore_index=True)

results.to_csv("hand_coded_results.csv", index=False)
print(results)
