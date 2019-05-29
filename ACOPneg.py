from baseProbAwareAgent import BaseProbAwareAgent
from constrProbAwareAgent import ConstrProbAwareAgent
import pandas as pd
from time import time
from pprint import pprint
from datetime import timedelta
from problog.logic import Term
from pprint import pprint
import multiprocessing as mp
from multiprocessing import Pool
from constraint import NoGood


def generateDummyIssues(A, B, issues, numberOfIssuesToGenerate):
    for i in range(numberOfIssuesToGenerate):
        issues["dummy{i}".format(i=i)] = [True, False]
        if i % 2 == 0:
            A.addOwnConstraint(NoGood("dummy{i}".format(i=i), "True"))
        else:
            B.addOwnConstraint(NoGood("dummy{i}".format(i=i), "True"))


def simulateACOPNeg(i):
    sim, dummyIssues = i
    print("simulating round {i}".format(i=sim))
    TerroristUtilities = {}
    NegeotiatorUtilities = {}
    issues = {}
    verbose = False
    generateDummyIssues(NegeotiatorUtilities,
                        TerroristUtilities, issues, dummyIssues)

    AgentT = ConstrProbAwareAgent(
        TerroristUtilities, [], -100, -100, name="negotiator")
    AgentN = ConstrProbAwareAgent(
        NegeotiatorUtilities, [], -100, -100, name="terrorist")
    AgentN.setIssues(issues)
    result = {}
    history = []
    t_start = time()
    AgentN.negotiate(AgentT)
    result['runTime'] = float(time()-t_start)

    result['success'] = AgentN.successful
    result['messageCount'] = AgentN.messageCount
    result['TStrat'] = AgentT.stratName
    result['Nstrat'] = AgentN.stratName
    result['totalGeneratedOffers'] = int(AgentT.totalOffersGenerated +
                                         AgentN.totalOffersGenerated)
    return result


numbOfSimulations = 5
numbOfDummyIssues = 8
start_time = time()
with Pool(1) as p:
    res = p.map(simulateACOPNeg, [(i, numbOfDummyIssues)
                                  for i in range(numbOfSimulations)])
    pd_res = pd.DataFrame(res)
    print(pd_res[
          ["messageCount", "totalGeneratedOffers", "runTime"]])
    print("total CPU time: {sum}".format(sum=pd_res.loc[:, "runTime"].sum()))
    print("Real world time: {t}".format(t=float(time()-start_time)))


# sims = simulateNNegs(hostageIssues, numbOfSimulations)
# print(sims)
# print("total running time: {t}s".format(t=sims.loc[:, "runTime"].sum()))
