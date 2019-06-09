from src.DTPAgent import DTPNegotiationAgent
import pandas as pd
from time import time
from multiprocessing import Pool
from src.constraint import NoGood
from numpy.random import normal, choice, seed
from random import randint
from uuid import uuid4

def generateDummyIssues(AUtilities, Aconstraints, BUtilities, Bconstraints, issues, numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent):
    for i in range(numberOfIssuesToGenerate):
        issues["dummy{i}".format(i=i)] = list(range(issueCardinality))
        for j in range(issueCardinality):
            AUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(10, 10)  # -(2**31)
        for j in range(issueCardinality):
            BUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(10, 10)  # -(2**31)  # normal(0,100)

    while len(Aconstraints) < numberOfConstraintsPerAgent:
        Aissue = choice(list(issues.keys()))
        AValue = choice(list(issues[Aissue]))
        Aconstraints.add(NoGood(Aissue, AValue))

    while len(Bconstraints) < numberOfConstraintsPerAgent:
        Bissue = choice(list(issues.keys()))
        BValue = choice(list(issues[Bissue]))
        Bconstraints.add(NoGood(Bissue, BValue))


def simulateACOPNeg(i):
    seed()
    sim, dummyIssues = i
    print("simulating round {i}".format(i=sim))
    TerroristUtilities = {}
    TerroristConstraints = set()
    NegeotiatorUtilities = {}
    NegotiatorConstraints = set()
    issues = {}
    numbOfConstraints = randint(0,issueCardinality-1)
    generateDummyIssues(NegeotiatorUtilities, NegotiatorConstraints,
                        TerroristUtilities,TerroristConstraints, issues, dummyIssues,issueCardinality, numbOfConstraints)
    AgentT = DTPNegotiationAgent(uuid4(),
        TerroristUtilities, [], 50, -1000, name="negotiator",reporting=False)
    AgentN = DTPNegotiationAgent(uuid4(),
        NegeotiatorUtilities, [], 50, -1000, name="terrorist",reporting=True)

    AgentN.verbose = 3
    AgentT.verbose = 3

    AgentN.setIssues(issues)
    for constr in NegotiatorConstraints:
        AgentN.addOwnConstraint(constr)

    for constr in TerroristConstraints:
        AgentT.addOwnConstraint(constr)



    result = {}
    t_start = time()
    try:
        AgentN.negotiate(AgentT)
    except RuntimeError:
        print(AgentN.constraintsSatisfiable)
        print(AgentN.getAllConstraints())
        print(AgentN.utilities)
    result['runTime'] = float(time()-t_start)

    result['success'] = AgentN.successful
    result['messageCount'] = AgentN.messageCount + AgentT.messageCount
    result['TStrat'] = AgentT.stratName
    result['Nstrat'] = AgentN.stratName
    result['numbOfConstraints'] = numbOfConstraints
    result['totalGeneratedOffers'] = int(AgentT.totalOffersGenerated +
                                         AgentN.totalOffersGenerated)
    print("Simulation {} finished! it contained {} constraints and finished in {} rounds".format(sim, numbOfConstraints,AgentN.messageCount))
    return result


numbOfSimulations = 1
numbOfDummyIssues = 3
issueCardinality = 3
numberOfConstraintsPerAgent = 0
start_time = time()
with Pool(1) as p:
    res = p.map(simulateACOPNeg, [(i, numbOfDummyIssues)
                                  for i in range(numbOfSimulations)])
    pd_res = pd.DataFrame(res)
    print(pd_res[
          ["messageCount", "totalGeneratedOffers","numbOfConstraints", "runTime"]])
    print("total CPU time: {sum}".format(sum=pd_res.loc[:, "runTime"].sum()))
    print("Real world time: {t}".format(t=float(time()-start_time)))

# sims = simulateNNegs(hostageIssues, numbOfSimulations)
# print(sims)
# print("total running time: {t}s".format(t=sims.loc[:, "runTime"].sum()))
