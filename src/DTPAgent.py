from constraintNegotiationAgent import ConstraintNegotiationAgent
import subprocess as sp
from os import remove, getcwd, getpid
from os.path import join, abspath, dirname
import re
from numpy import isclose
from numpy.random import choice


class DTPNegotiationAgent(ConstraintNegotiationAgent):
    def __init__(self, uuid, utilities, kb, reservationValue, nonAgreementCost, issues=None, maxRounds=10000, verbose=0,
                 name="", reporting=True, meanUtility=0,stdUtility=0):
        super().__init__(uuid, utilities, kb, reservationValue, nonAgreementCost, issues=issues, maxRounds=maxRounds,
                         verbose=verbose,
                         name=name, reporting=reporting, meanUtility=meanUtility,stdUtility=stdUtility)
        self.stratName = "DTP"
        self.generatedOffers = []

    def non_leaky_dtproblog(self, model):
        # using the python implementation of problog causes memory leaks
        # so we use the commandline interface seperately to avoid this as a temp fix
        self.totalOffersGenerated += 1
        modelPath = abspath(join(dirname(__file__), '../models/temp_model_{}.pl'.format(getpid())))
        if self.verbose >= 3:
            print("{} is calculating dtp model: {}".format(self.agentName, model))

        with open(modelPath, "w") as temp_file:
            temp_file.write(model)

        process = sp.Popen(["problog", "dt", modelPath, "--verbose"], stdout=sp.PIPE)
        output, error = process.communicate()
        decodedOutput = output.decode("ascii")
        score = float(re.search(r"SCORE: (-?\d+\.\d+)", decodedOutput).group(1))

        ans = {}
        for string in decodedOutput.split("\n"):
            if string and not re.search("[INFO]", string):
                key, prob = string.strip().split(":\t")
                ans[key] = float(prob)

        # for issue in self.issues.keys:
        #     if not issue in ans

        remove(modelPath)
        return ans, score

    def compileDTProblogModel(self):
        decisionFactsString = self.formatDTProblogStrat()
        utilityString = self.formatUtilityString()
        kbString = "\n".join(self.KB) + "\n"
        return decisionFactsString + kbString + utilityString

    def formatDTProblogStrat(self):
        returnString = ""
        for issue in self.stratDict.keys():
            atomList = []
            for value in self.stratDict[issue].keys():
                if "." in str(value):
                    atomList.append("?::'{issue}_{val}'".format(
                        issue=issue, val=value))
                else:
                    atomList.append("?::{issue}_{val}".format(
                        issue=issue, val=value))

            returnString += ";".join(atomList) + ".\n"
        return returnString

    def formatUtilityString(self):
        returnString = ""
        for u, r in self.utilities.items():
            returnString += "utility({},{}).\n".format(u, r)

        offerCounter = 0
        for offer, score in self.generatedOffers:
            atomList = []
            for atom, val in offer.items():
                if isclose(val, 1):
                    atomList.append(atom)
            returnString += "offer{} :- {}.\n".format(offerCounter, ",".join(atomList))
            returnString += "utility(offer{},{}).\n".format(offerCounter, -score + self.nonAgreementCost)
            offerCounter += 1

        return returnString

    def generateOffer(self):
        queryOutput, score = self.non_leaky_dtproblog(self.compileDTProblogModel())
        if self.verbose >= 3:
            print("{} generated offer: {}".format(self.agentName, self.atomDictToNestedDict(queryOutput)))

        # if there are no acceptable offers left we should terminate
        if score < self.reservationValue:
            return None

        self.generatedOffers.append((queryOutput, score))
        generatedOffer = self.atomDictToNestedDict(queryOutput)

        # if dtproblog didn't choose a value we'll just randomly choose one since it makes no difference
        # but we need to choose according to the strat dict so we don't choose a constrained value
        listedStrat = {}
        for issue in self.stratDict.keys():
            listedStrat[issue] = list(map(list, zip(*self.stratDict[issue].items())))

        for issue in generatedOffer.keys():
            if isclose(sum(generatedOffer[issue].values()),0):
                chosenValue = str(choice(listedStrat[issue][0], 1, p=listedStrat[issue][1])[0])
                generatedOffer[issue] = {key: 0 for key in self.stratDict[issue].keys()}
                generatedOffer[issue][chosenValue] = 1

        return generatedOffer
