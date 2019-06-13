from DTPAgent import DTPNegotiationAgent
from constraintNegotiationAgent import ConstraintNegotiationAgent
from randomNegotiationAgent import RandomNegotiationAgent
import pandas as pd
from time import time
from multiprocessing import Pool
from constraint import AtomicConstraint
from numpy.random import normal, choice, seed
from numpy import arange
from uuid import uuid4
import itertools as it
from notify import try_except_notify


def generateNegotiation(numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent,
                        meanUtility, stdUtility, strat):

    negotiationID = uuid4()
    TerroristUtilities = {}
    NegotiatorUtilities = {}
    issues = {}
    reservationValue = 50
    nonAgreementCost = -(2**24) # just a really big number

    for i in range(numberOfIssuesToGenerate):
        issues["dummy{i}".format(i=i)] = list(range(issueCardinality))
        for j in range(issueCardinality):
            TerroristUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(meanUtility, stdUtility)
        for j in range(issueCardinality):
            NegotiatorUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(meanUtility, stdUtility)

    if strat == "Random":
        terrorist = RandomNegotiationAgent(negotiationID,TerroristUtilities,[],reservationValue,nonAgreementCost,
                                           issues,name="terrorist",meanUtility=meanUtility,stdUtility=stdUtility)
        negotiator = RandomNegotiationAgent(negotiationID, NegotiatorUtilities,[],reservationValue,nonAgreementCost,
                                            issues,name="negotiatior",reporting=True,meanUtility=meanUtility,stdUtility=stdUtility)
    elif strat == "Constrained":
        terrorist = ConstraintNegotiationAgent(negotiationID,TerroristUtilities,[],reservationValue,nonAgreementCost,
                                               issues=issues,name="terrorist",meanUtility=meanUtility,stdUtility=stdUtility)
        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
            Tissue = choice(list(issues.keys()))
            TValue = choice(list(issues[Tissue]))
            terrorist.addOwnConstraint(AtomicConstraint(Tissue, TValue))

        negotiator = ConstraintNegotiationAgent(negotiationID, NegotiatorUtilities, [], reservationValue, nonAgreementCost,
                                            issues, name="negotiatior", reporting=True,meanUtility=meanUtility,stdUtility=stdUtility)
        while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
            Nissue = choice(list(issues.keys()))
            NValue = choice(list(issues[Nissue]))
            negotiator.addOwnConstraint(AtomicConstraint(Nissue, NValue))

    else:
        terrorist = DTPNegotiationAgent(negotiationID, TerroristUtilities, [], reservationValue,
                                               nonAgreementCost,
                                               issues=issues, name="terrorist",meanUtility=meanUtility,stdUtility=stdUtility)
        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
            Tissue = choice(list(issues.keys()))
            TValue = choice(list(issues[Tissue]))
            terrorist.addOwnConstraint(AtomicConstraint(Tissue, TValue))

        negotiator = DTPNegotiationAgent(negotiationID, NegotiatorUtilities, [], reservationValue,
                                                nonAgreementCost,
                                                issues, name="negotiatior", reporting=True,meanUtility=meanUtility,stdUtility=stdUtility)
        while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
            Nissue = choice(list(issues.keys()))
            NValue = choice(list(issues[Nissue]))
            negotiator.addOwnConstraint(AtomicConstraint(Nissue, NValue))

    return negotiator,terrorist


def simulateNegotiation(config):

    seed()
    numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent, meanUtility, stdUtility, strat = config

    # avoid rerunning the same simulations multiple times
    if strat == "Random" and numberOfConstraintsPerAgent > 0:
        return
    print(
        "starting simulation: numbOfIssues={}, issueCard={}, numbOfConstraints={}, meanUtil={}, stdUtil={}, strat={}".format(
            *config))

    negotiator, terrorist = generateNegotiation(numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent,
                        meanUtility, stdUtility, strat)

    negotiator.negotiate(terrorist)
    if negotiator.successful:
        print("simulation with config numbOfIssues={}, issueCard={}, numbOfConstraints={}, meanUtil={}, stdUtil={}, strat={} finished successfully!".format(*config))
    else:
        print("simulation with config numbOfIssues={}, issueCard={}, numbOfConstraints={}, meanUtil={}, stdUtil={}, strat={} finished unsuccessfully!".format(*config))




@try_except_notify
def parallelSimulation():
    trailsPerConfig = 5
    means = [100]
    stds = [10]
    issueCardinalities = [3]
    issueCounts = [3]
    constraintCounts = [0,2]
    strats = ["Random", "Constrained","DTP"]

    # means = arange(-50,50,10)
    # stds = arange(1,20,5)
    # issueCardinalities = range(1,7)
    # issueCounts = range(1,7)
    # constraintCounts = range(0,15)
    # strats = ["Random", "Constrained", "DTP"]

    for _ in range(trailsPerConfig):
        configs = it.product(*[issueCounts, issueCardinalities, constraintCounts, means, stds, strats])
        with Pool(15) as p:
            p.map(simulateNegotiation, configs)
        # simulateNegotiation(next(configs))


parallelSimulation(1)
