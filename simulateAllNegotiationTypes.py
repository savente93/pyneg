from multiprocessing import Pool
from uuid import uuid4

from numpy import arange
from numpy.random import normal, seed, poisson
from scipy.stats import norm

from DTPAgent import DTPNegotiationAgent
from constraintNegotiationAgent import ConstraintNegotiationAgent
from notify import try_except_notify
from randomNegotiationAgent import RandomNegotiationAgent


def generate_negotiation(number_of_issues_to_generate, issue_cardinality,
                         mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b, strat):
    negotiation_id = uuid4()
    terrorist_utilities = {}
    negotiator_utilities = {}
    issues = {}
    non_agreement_cost = -(2 ** 24)  # just a really big number

    for i in range(number_of_issues_to_generate):
        issues["dummy{i}".format(i=i)] = list(range(issue_cardinality))
        for j in range(issue_cardinality):
            terrorist_utilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(mu_a, sigma_b)
        for j in range(issue_cardinality):
            negotiator_utilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(mu_b, sigma_b)

    if strat == "Random":
        terrorist = RandomNegotiationAgent(negotiation_id, terrorist_utilities, [], rho_a, non_agreement_cost,
                                           issues, name="terrorist", mean_utility=mu_a, std_utility=sigma_a)
        negotiator = RandomNegotiationAgent(negotiation_id, negotiator_utilities, [], rho_b, non_agreement_cost,
                                            issues, name="negotiator", reporting=True, mean_utility=mu_b,
                                            std_utility=sigma_b)
    elif strat == "Constrained":
        terrorist = ConstraintNegotiationAgent(negotiation_id, terrorist_utilities, [], rho_a, non_agreement_cost,
                                               issues=issues, name="terrorist", mean_utility=mu_a,
                                               std_utility=sigma_b, constraint_threshold=0)
        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        # while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
        #     Tissue = choice(list(issues.keys()))
        #     TValue = choice(list(issues[Tissue]))
        #     terrorist.addOwnConstraint(AtomicConstraint(Tissue, TValue))

        negotiator = ConstraintNegotiationAgent(negotiation_id, negotiator_utilities, [], rho_b, non_agreement_cost,
                                                issues, name="negotiator", reporting=True, mean_utility=mu_b,
                                                std_utility=sigma_b, constraint_threshold=0)
        # while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
        #     Nissue = choice(list(issues.keys()))
        #     NValue = choice(list(issues[Nissue]))
        #     negotiator.addOwnConstraint(AtomicConstraint(Nissue, NValue))

    else:
        terrorist = DTPNegotiationAgent(negotiation_id, terrorist_utilities, [], rho_a,
                                        non_agreement_cost, issues=issues, name="terrorist",
                                        mean_utility=mu_a, std_utility=sigma_b)

        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        # while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
        #     Tissue = choice(list(issues.keys()))
        #     TValue = choice(list(issues[Tissue]))
        #     terrorist.addOwnConstraint(AtomicConstraint(Tissue, TValue))

        negotiator = DTPNegotiationAgent(negotiation_id, negotiator_utilities, [], rho_b,
                                         non_agreement_cost, issues, name="negotiator",
                                         reporting=True, mean_utility=mu_b,
                                         std_utility=sigma_b)
        # while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
        #     Nissue = choice(list(issues.keys()))
        #     NValue = choice(list(issues[Nissue]))
        #     negotiator.addOwnConstraint(AtomicConstraint(Nissue, NValue))

    return negotiator, terrorist


def simulate_negotiation(config):
    seed()
    number_of_issues_to_generate, issue_cardinality, mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b, strat = config

    print(
        "starting simulation: numbOfIssues={}, issueCard={}, mu_a={},sigma_a={},rho_a={},mu_b={},sigma_b={},rho_b={},strat={}".format(
            *config))

    negotiator, terrorist = generate_negotiation(number_of_issues_to_generate, issue_cardinality,
                                                mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b, strat)

    negotiator.negotiate(terrorist)
    if negotiator.successful:
        print(
            "simulation with config numbOfIssues={}, issueCard={}, mu_a={},sigma_a={},rho_a={},mu_b={},sigma_b={},rho_b={},strat={} finished successfully!".format(
                *config))
    else:
        print(
            "simulation with config numbOfIssues={}, issueCard={}, mu_a={},sigma_a={},rho_a={},mu_b={},sigma_b={},rho_b={},strat={} finished unsuccessfully!".format(
                *config))


def difficulty(n, m, mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b):
    if sigma_a <= 0 or sigma_b <= 0:
        return -1
    return 1 - (norm(0, 1).cdf((rho_a - n * m * mu_a) / (n * m * sigma_a)) * norm(0, 1).cdf(
        (rho_b - n * m * mu_b) / (n * m * sigma_b)))


def find_diff_config(diff, strat="Random"):
    n = 1
    m = 1
    mu_a = 0
    sigma_a = 1
    rho_a = 0
    mu_b = 0
    sigma_b = 1
    rho_b = 0
    while abs(difficulty(n, m, mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b) - diff) >= 0.001:
        n = poisson(3) + 1  # , 15)
        m = poisson(3) + 1  # , 15)
        mu_a = normal(0, 10)
        sigma_a = abs(normal(0, 10))
        rho_a = normal(0, 10)
        mu_b = normal(0, 10)
        sigma_b = abs(normal(0, 10))
        rho_b = normal(0, 10)

    return n, m, mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b, strat


def generate_configs(lst, trailsPerDifficulty, range, step, strat="Random"):
    for _ in arange(trailsPerDifficulty):
        for diff in [0.9]:  # arange(0.1, range+step, step):
            config = find_diff_config(diff, strat=strat)
            lst.append(config)
    return lst


@try_except_notify
def parallel_simulation():
    trails_per_config = 1
    # means = [-50]
    # stds = [10]
    # issue_cardinalities = [3]
    # issue_counts = [3]
    # strats = ["Random", "Constrained", "DTP"]

    # means = arange(-50,50,10)
    # stds = arange(1,20,5)
    # issue_cardinalities = range(1,7)
    # issue_counts = range(1,7)
    # constraint_counts = range(0,15)
    configs = []
    configs = generate_configs(configs, trails_per_config, 0.1, 0.1, strat="Random")
    configs = generate_configs(configs, trails_per_config, 0.1, 0.1, strat="Constrained")
    configs = generate_configs(configs, trails_per_config, 0.1, 0.1, strat="DTP")
    # for _ in range(trailsPerConfig):

    with Pool(15) as p:
        p.map(simulate_negotiation, configs)


parallel_simulation(1)
