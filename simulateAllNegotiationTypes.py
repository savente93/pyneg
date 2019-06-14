from DTPAgent import DTPNegotiationAgent
from constraintNegotiationAgent import ConstraintNegotiationAgent
from randomNegotiationAgent import RandomNegotiationAgent
import pandas as pd
from time import time
from multiprocessing import Pool
from constraint import AtomicConstraint
from numpy.random import normal, choice, seed, poisson
from numpy import arange
from uuid import uuid4
import itertools as it
from notify import try_except_notify
from scipy.stats import norm
from random import randint


def generateNegotiation(numberOfIssuesToGenerate, issueCardinality,
                        mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b, strat):
    negotiationID = uuid4()
    TerroristUtilities = {}
    NegotiatorUtilities = {}
    issues = {}
    nonAgreementCost = -(2 ** 24)  # just a really big number

    for i in range(numberOfIssuesToGenerate):
        issues["dummy{i}".format(i=i)] = list(range(issueCardinality))
        for j in range(issueCardinality):
            TerroristUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(mu_a, sigma_b)
        for j in range(issueCardinality):
            NegotiatorUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(mu_b, sigma_b)

    if strat == "Random":
        terrorist = RandomNegotiationAgent(negotiationID, TerroristUtilities, [], rho_a, nonAgreementCost,
                                           issues, name="terrorist", meanUtility=mu_a, stdUtility=sigma_a)
        negotiator = RandomNegotiationAgent(negotiationID, NegotiatorUtilities, [], rho_b, nonAgreementCost,
                                            issues, name="negotiatior", reporting=True, meanUtility=mu_b,
                                            stdUtility=sigma_b)
    elif strat == "Constrained":
        terrorist = ConstraintNegotiationAgent(negotiationID, TerroristUtilities, [], rho_a, nonAgreementCost,
                                               issues=issues, name="terrorist", meanUtility=mu_a,
                                               stdUtility=sigma_b, constraintThreshold=0)
        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        # while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
        #     Tissue = choice(list(issues.keys()))
        #     TValue = choice(list(issues[Tissue]))
        #     terrorist.addOwnConstraint(AtomicConstraint(Tissue, TValue))


        negotiator = ConstraintNegotiationAgent(negotiationID, NegotiatorUtilities, [], rho_b, nonAgreementCost,
                                                issues, name="negotiatior", reporting=True, meanUtility=mu_b,
                                                stdUtility=sigma_b, constraintThreshold=0)
        # while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
        #     Nissue = choice(list(issues.keys()))
        #     NValue = choice(list(issues[Nissue]))
        #     negotiator.addOwnConstraint(AtomicConstraint(Nissue, NValue))

    else:
        terrorist = DTPNegotiationAgent(negotiationID, TerroristUtilities, [], rho_a,
                                        nonAgreementCost,
                                        issues=issues, name="terrorist", meanUtility=mu_a, stdUtility=sigma_b)

        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        # while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
        #     Tissue = choice(list(issues.keys()))
        #     TValue = choice(list(issues[Tissue]))
        #     terrorist.addOwnConstraint(AtomicConstraint(Tissue, TValue))

        negotiator = DTPNegotiationAgent(negotiationID, NegotiatorUtilities, [], rho_b,
                                         nonAgreementCost,
                                         issues, name="negotiatior", reporting=True, meanUtility=mu_b,
                                         stdUtility=sigma_b)
        # while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
        #     Nissue = choice(list(issues.keys()))
        #     NValue = choice(list(issues[Nissue]))
        #     negotiator.addOwnConstraint(AtomicConstraint(Nissue, NValue))

    return negotiator, terrorist


def simulateNegotiation(config):
    seed()
    numberOfIssuesToGenerate, issueCardinality, mu_a,sigma_a,rho_a,mu_b,sigma_b,rho_b, strat = config

    print(
        "starting simulation: numbOfIssues={}, issueCard={}, mu_a={},sigma_a={},rho_a={},mu_b={},sigma_b={},rho_b={},strat={}".format(
            *config))

    negotiator, terrorist = generateNegotiation(numberOfIssuesToGenerate, issueCardinality,
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


def findDiffConfig(diff, strat="Random"):
    n = 1
    m = 1
    mu_a = 0
    sigma_a = 1
    rho_a = 0
    mu_b = 0
    sigma_b = 1
    rho_b = 0
    while abs(difficulty(n, m, mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b) - diff) >= 0.001:
        n = poisson(3)+1#, 15)
        m = poisson(3)+1#, 15)
        mu_a = normal(0, 10)
        sigma_a = abs(normal(0, 10))
        rho_a = normal(0, 10)
        mu_b = normal(0, 10)
        sigma_b = abs(normal(0, 10))
        rho_b = normal(0, 10)

    return n, m, mu_a, sigma_a, rho_a, mu_b, sigma_b, rho_b, strat


def generateConfigs(lst,trailsPerDifficulty,range,step, strat="Random"):
    for _ in arange(trailsPerDifficulty):
        for diff in [0.9]: #arange(0.1, range+step, step):
            config = findDiffConfig(diff,strat=strat)
            lst.append(config)
    return lst

@try_except_notify
def parallelSimulation():
    trailsPerConfig = 1
    # means = [-50]
    # stds = [10]
    # issueCardinalities = [3]
    # issueCounts = [3]
    strats = ["Random", "Constrained", "DTP"]

    # means = arange(-50,50,10)
    # stds = arange(1,20,5)
    # issueCardinalities = range(1,7)
    # issueCounts = range(1,7)
    # constraintCounts = range(0,15)
    configs = []
    configs = generateConfigs(configs, trailsPerConfig, 0.1, 0.1, strat="Random")
    configs = generateConfigs(configs, trailsPerConfig, 0.1, 0.1, strat="Constrained")
    configs = generateConfigs(configs, trailsPerConfig, 0.1, 0.1, strat="DTP")
    # for _ in range(trailsPerConfig):

    with Pool(15) as p:
        p.map(simulateNegotiation, configs)


parallelSimulation(1)
