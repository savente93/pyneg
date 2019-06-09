from src.DTPAgent import DTPNegotiationAgent
from src.constraintNegotiationAgent import ConstraintNegotiationAgent
from src.randomNegotiationAgent import RandomNegotiationAgent
import pandas as pd
from time import time
from multiprocessing import Pool
from src.constraint import NoGood
from numpy.random import normal, choice, seed
from numpy import arange
from uuid import uuid4
import itertools as it
from src.notify import try_except_notify


def generateNegotiation(numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent,
                        meanUtility, stdUtility, strat):

    # avoid rerunning the same simulations multiple times
    if strat == "Random" and numberOfConstraintsPerAgent > 0:
        return

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
                                           issues,name="terrorist")
        negotiator = RandomNegotiationAgent(negotiationID, NegotiatorUtilities,[],reservationValue,nonAgreementCost,
                                            issues,name="negotiatior",reporting=True)
    elif strat == "Constrained":
        terrorist = ConstraintNegotiationAgent(negotiationID,TerroristUtilities,[],reservationValue,nonAgreementCost,
                                               issues=issues,name="terrorist")
        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
            Tissue = choice(list(issues.keys()))
            TValue = choice(list(issues[Tissue]))
            terrorist.addOwnConstraint(NoGood(Tissue, TValue))

        negotiator = ConstraintNegotiationAgent(negotiationID, NegotiatorUtilities, [], reservationValue, nonAgreementCost,
                                            issues, name="negotiatior", reporting=True)
        while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
            Nissue = choice(list(issues.keys()))
            NValue = choice(list(issues[Nissue]))
            negotiator.addOwnConstraint(NoGood(Nissue, NValue))

    else:
        terrorist = DTPNegotiationAgent(negotiationID, TerroristUtilities, [], reservationValue,
                                               nonAgreementCost,
                                               issues=issues, name="terrorist")
        # use while loop instead of a for loop to ensure generating the same constraint doesn't matter
        while len(terrorist.ownConstraints) < numberOfConstraintsPerAgent:
            Tissue = choice(list(issues.keys()))
            TValue = choice(list(issues[Tissue]))
            terrorist.addOwnConstraint(NoGood(Tissue, TValue))

        negotiator = DTPNegotiationAgent(negotiationID, NegotiatorUtilities, [], reservationValue,
                                                nonAgreementCost,
                                                issues, name="negotiatior", reporting=True)
        while len(negotiator.ownConstraints) < numberOfConstraintsPerAgent:
            Nissue = choice(list(issues.keys()))
            NValue = choice(list(issues[Nissue]))
            negotiator.addOwnConstraint(NoGood(Nissue, NValue))

    return negotiator,terrorist


def simulateNegotiation(config):
    seed()
    print("starting simulation: numbOfIssues={}, issueCard={}, numbOfConstraints={}, meanUtil={}, stdUtil={}, strat={}".format(*config))
    numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent, meanUtility, stdUtility, strat = config

    negotiator, terrorist = generateNegotiation(numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent,
                        meanUtility, stdUtility, strat)

    negotiator.negotiate(terrorist)
    print("simulation with config numbOfIssues={}, issueCard={}, numbOfConstraints={}, meanUtil={}, stdUtil={}, strat={} finished!".format(*config))

# means = arange(-50,50,10)
# stds = arange(1,20,5)
# issueCardinalities = range(1,15)
# issueCounts = range(1,15)
# constraintCounts = range(0,15)
# strats = ["Random", "Constrained","DTP"]

@try_except_notify
def parallelSimulation():
    trailsPerConfig = 5
    means = [100]
    stds = [10]
    issueCardinalities = [3]
    issueCounts = [3]
    constraintCounts = [2]
    strats = ["Constrained"]

    for _ in range(trailsPerConfig):
        configs = it.product(*[issueCounts, issueCardinalities, constraintCounts, means, stds, strats])
        with Pool() as p:
            res = p.map(simulateNegotiation, configs)


parallelSimulation(1)