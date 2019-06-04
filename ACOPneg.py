from constrProbAwareAgent import ConstrProbAwareAgent
import pandas as pd
from time import time
from multiprocessing import Pool
from constraint import NoGood
from numpy.random import normal, choice

def generateDummyIssues(AUtilities, Aconstraints, BUtilities, Bconstraints, issues, numberOfIssuesToGenerate, issueCardinality, numberOfConstraintsPerAgent):
    for i in range(numberOfIssuesToGenerate):
        issues["dummy{i}".format(i=i)] = list(range(issueCardinality))
        for j in range(issueCardinality):
            AUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(10, 10)  # -(2**31)
        for j in range(issueCardinality):
            BUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(10, 10)  # -(2**31)  # normal(0,100)

    print(AUtilities)
    print(BUtilities)

    while len(Aconstraints) < numberOfConstraintsPerAgent:
        Aissue = choice(list(issues.keys()))
        AValue = choice(list(issues[Aissue]))
        Aconstraints.add(NoGood(Aissue, AValue))

    while len(Bconstraints) < numberOfConstraintsPerAgent:
        Bissue = choice(list(issues.keys()))
        BValue = choice(list(issues[Bissue]))
        Bconstraints.add(NoGood(Bissue, BValue))


def simulateACOPNeg(i):
    sim, dummyIssues = i
    print("simulating round {i}".format(i=sim))
    TerroristUtilities = {}
    TerroristConstraints = set()
    NegeotiatorUtilities = {}
    NegotiatorConstraints = set()
    issues = {}
    generateDummyIssues(NegeotiatorUtilities, NegotiatorConstraints,
                        TerroristUtilities,TerroristConstraints, issues, dummyIssues,issueCardinality, numberOfConstraintsPerAgent)
    AgentT = ConstrProbAwareAgent(
        TerroristUtilities, [], 50, -1000, name="negotiator")
    AgentN = ConstrProbAwareAgent(
        NegeotiatorUtilities, [], 50, -1000, name="terrorist")

    # AgentN.verbose = 3
    # AgentT.verbose = 2

    AgentN.setIssues(issues)
    print("Negotiator constraints: {}".format(NegotiatorConstraints))
    print("Terrorist constraints: {}".format(TerroristConstraints))
    for constr in NegotiatorConstraints:
        AgentN.addOwnConstraint(constr)

    for constr in TerroristConstraints:
        AgentT.addOwnConstraint(constr)



    result = {}
    t_start = time()
    AgentN.negotiate(AgentT)
    result['runTime'] = float(time()-t_start)

    result['success'] = AgentN.successful
    result['messageCount'] = AgentN.messageCount
    result['TStrat'] = AgentT.stratName
    result['Nstrat'] = AgentN.stratName
    result['totalGeneratedOffers'] = int(AgentT.totalOffersGenerated +
                                         AgentN.totalOffersGenerated)
    print(AgentN.transcript)
    return result


numbOfSimulations = 5
numbOfDummyIssues = 8
issueCardinality = 3
numberOfConstraintsPerAgent = 10
start_time = time()
# with Pool(1) as p:
res = list(map(simulateACOPNeg, [(i, numbOfDummyIssues)
                              for i in range(numbOfSimulations)]))
pd_res = pd.DataFrame(res)
print(pd_res[
      ["messageCount", "totalGeneratedOffers", "runTime"]])
print("total CPU time: {sum}".format(sum=pd_res.loc[:, "runTime"].sum()))
print("Real world time: {t}".format(t=float(time()-start_time)))


# sims = simulateNNegs(hostageIssues, numbOfSimulations)
# print(sims)
# print("total running time: {t}s".format(t=sims.loc[:, "runTime"].sum()))
