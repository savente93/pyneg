from randomNegotiationAgent import RandomNegotiationAgent
import pandas as pd
from time import time
from multiprocessing import Pool
from numpy.random import normal, seed
from uuid import uuid4


def generateDummyIssues(AUtilities, BUtilities, issues, numberOfIssuesToGenerate, issueCardinality):
    for i in range(numberOfIssuesToGenerate):
        issues["dummy{i}".format(i=i)] = range(issueCardinality)
        for j in range(issueCardinality):
            AUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(10, 10)  # -(2**31)
        for j in range(issueCardinality):
            BUtilities["dummy{i}_{j}".format(
                i=i, j=j)] = normal(10, 10)  # -(2**31)  # normal(0,100)


def simulateAOPNeg(i):
    seed()
    sim, dummyIssues = i
    print("simulating round {i}".format(i=sim))
    TerroristUtilities = {}
    NegeotiatorUtilities = {}
    issues = {}
    generateDummyIssues(NegeotiatorUtilities,
                        TerroristUtilities, issues, dummyIssues, issueCardinality)

    AgentT = RandomNegotiationAgent( uuid4(),
        TerroristUtilities, [], 50, -1000, name="negotiator",reporting=True)
    AgentN = RandomNegotiationAgent( uuid4(),
        NegeotiatorUtilities, [], 50, -1000, name="terrorist",reporting=True)
    AgentN.setIssues(issues)
    # AgentN.verbose = 3
    # AgentT.verbose = 3
    result = {}
    t_start = time()
    AgentN.negotiate(AgentT)
    result['runTime'] = float(time()-t_start)
    result['success'] = AgentN.successful
    result['messageCount'] = AgentN.messageCount
    result['TStrat'] = AgentT.stratName
    result['Nstrat'] = AgentN.stratName
    result['Nutil'] = AgentN.calcOfferUtility(AgentN.transcript[-1].offer)
    result['Tutil'] = AgentT.calcOfferUtility(AgentT.transcript[-1].offer)
    result['totalGeneratedOffers'] = int(AgentT.totalOffersGenerated +
                                         AgentN.totalOffersGenerated)
    print("simulation {i} finished!".format(i=sim))
    return result


numbOfSimulations = 4
numbOfDummyIssues = 5
issueCardinality = 5
start_time = time()
# res = list(map(simulateAOPNeg, [(i, numbOfDummyIssues)
#                                 for i in range(numbOfSimulations)]))
# pd_res = pd.DataFrame(res)
# pd_res.to_csv("AOPneg.log")
# print(pd_res[
#     ["success", "messageCount", "totalGeneratedOffers", 'Nutil', 'Tutil', "runTime"]])
# print("total CPU time: {sum}".format(sum=pd_res.loc[:, "runTime"].sum()))
# print("Real world time: {t}".format(t=float(time()-start_time)))


with Pool() as p:
    res = p.map(simulateAOPNeg, [(i, numbOfDummyIssues)
                                 for i in range(numbOfSimulations)])
    pd_res = pd.DataFrame(res)
    pd_res.to_csv("AOPneg.log")
    print(pd_res[
          ["success", "messageCount", "totalGeneratedOffers", 'Nutil', 'Tutil', "runTime"]])
    print("total CPU time: {sum}".format(sum=pd_res.loc[:, "runTime"].sum()))
    print("Real world time: {t}".format(t=float(time()-start_time)))


# sims = simulateNNegs(hostageIssues, numbOfSimulations)
# print(sims)
# print("total running time: {t}s".format(t=sims.loc[:, "runTime"].sum()))
