from numpy import isclose
from re import search, sub
from message import Message
from numpy.random import choice
import subprocess as sp
from os import remove, getcwd, getpid
from os.path import join, abspath, dirname
from pandas import Series
from time import time

class RandomNegotiationAgent():
    def __init__(self,uuid, utilities, kb, reservationValue, nonAgreementCost, issues=None, maxRounds=100, smart=True, name="",  verbose=0, reporting=False, meanUtility=0,stdUtility=0):
        self.verbose = verbose
        self.uuid = uuid
        self.reporting = reporting
        self.maxRounds = maxRounds
        self.nonAgreementCost = nonAgreementCost
        self.successful = False
        self.negotiationActive = False
        self.totalOffersGenerated = 0
        self.messageCount = 0
        self.stratName = "Random"
        self.agentName = name
        self.reservationValue = reservationValue
        self.stratDict = {}
        self.transcript = []
        self.nextMessageToSend = None
        self.opponent = None
        self.startTime = 0
        self.meanUtility = meanUtility # for results collection only not used internally
        self.stdUtility = stdUtility # for results collection only not used internally
        # self.utilityCache = {}
        if issues:
            self.setIssues(issues)

        self.maxGenerationTries = 500

        self.setUtilities(utilities)
        self.KB = kb
        self.smart = smart

    def receiveNegotiationRequest(self, opponent, issues):
       # allows others to initiate negotiations with us
       # we allways accept calls for negotiation if we can init propperly
        try:
            self.setupNegotiation(issues)
            self.opponent = opponent
            return True
        except:
            # something went wrong setting up so reject request
            print("{} failed to setup negotiation propperly".format(self.agentName))
            return False

    def callForNegotiation(self, opponent, issues):
        # allows us to initiate negotiations with others
        response = opponent.receiveNegotiationRequest(self, issues)
        if response:
            self.opponent = opponent
        return response

    def shouldTerminate(self, msg):
        return self.messageCount > self.maxRounds

    def sendMessage(self, opponent, msg):
        self.messageCount += 1
        if self.verbose >= 2:
            print("{} is sending {}".format(self.agentName, msg))
        opponent.receiveMessage(msg)


    def negotiate(self, opponent):
        # self is assumed to have setup the negotiation (including issues) beforehand
        self.negotiationActive = self.callForNegotiation(opponent, self.issues)

        # make initial offer
        # if self.negotiationActive:
        #     oppResponse = opponent.receiveMessage(self.generateOfferMessage())
        self.startTime = time()
        while self.negotiationActive:
            self.nextMessageToSend = self.generateNextMessageFromTranscript()
            if self.nextMessageToSend:
                opponent.receiveMessage(self.nextMessageToSend)
                self.receiveResponse(opponent)

        return self.successful

    def receiveResponse(self, sender):
        response = sender.generateNextMessageFromTranscript()
        self.recordMessage(response)


    def recordMessage(self, msg):
        if msg:
            self.messageCount += 1
            self.transcript.append(msg)

    def generateNextMessageFromTranscript(self):
        try:
            lastMessage = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self.generateOfferMessage()

        if lastMessage.isAcceptance():
            self.negotiationActive = False
            self.successful = True
            self.report()
            return None

        if lastMessage.isTermination():
            self.negotiationActive = False
            self.successful = False
            self.report()
            return None

        if self.shouldTerminate(lastMessage):
            self.negotiationActive = False
            self.successful = False
            self.report()
            return Message(self.agentName, self.opponent.agentName, "terminate", lastMessage.offer)

        if self.accepts(lastMessage.offer):
            self.negotiationActive = False
            self.successful = True
            self.report()
            return Message(self.agentName, self.opponent.agentName, "accept", lastMessage.offer)

        return self.generateOfferMessage()

    def setupNegotiation(self, issues):
        if self.verbose >= 1:
            print("{} is setting up the negotiation issues: {}".format(
                self.agentName, issues))
        self.setIssues(issues)
        self.initUniformStrategy()
        if self.verbose >= 1:
            print("{} Starting utilities: {}".format(
                self.agentName, self.utilities))
            print("{} Starting strattegy: {}".format(
                self.agentName, self.stratDict))


    def report(self):
        if self.verbose >= 1:
            if self.successful:
                print("Negotiation suceeded after {} rounds!".format(
                    self.messageCount))
            else:
                print("Negotiation failed after {} rounds!".format(
                    self.messageCount))
        if self.reporting:

            log = Series()
            log.rename(self.uuid)
            log['runtime'] =  time() - self.startTime
            log['success'] = self.successful
            log['totalMessageCount'] = self.messageCount + self.opponent.messageCount
            log['numbOfOwnConstraints'] = 0
            log['numbOfDiscoveredConstraints'] = 0
            log['strat'] = self.stratName
            log['opponentStrat'] = self.opponent.stratName
            log['utility'] = self.calcOfferUtility(self.transcript[-1].offer)
            log['opponentUtility'] = self.opponent.calcOfferUtility(self.transcript[-1].offer)
            log['totalGeneratedOffers'] = self.totalOffersGenerated + self.opponent.totalOffersGenerated
            log['issueCount'] = len(self.issues)
            log['issueCardinality'] = len(next(iter(self.issues))) # issue cardinality is uniform
            log['meanUtility'] = self.meanUtility
            log['stdUtility'] = self.stdUtility
            log.to_csv(abspath(join(dirname(__file__),"logs/{}.log".format(self.uuid))), header=0)

    def receiveMessage(self, msg):
        if self.verbose >= 1:
            print("{}: received message: {}".format(self.agentName, msg))
        self.recordMessage(msg)

    def setIssues(self, issues):
        self.decisionFacts = []
        self.stratDict = {}
        for issue, lst in issues.items():
            if "_" in str(issue) or "'" in str(issue):
                raise ValueError("Issue names should not contain _")
            for val in lst:
                if "_" in str(val) or "'" in str(val):
                    raise ValueError("Issue names should not contain _")

        self.issues = {key: list(map(str, issues[key]))
                       for key in issues.keys()}
        self.generateDecisionFacts()
        self.initUniformStrategy()
        # TODO must find a way to avoid having to clear the KB every time a new issue is raised
        self.KB = []

    def isStratValid(self, strat):
        # strat should have something on all issues
        for issue in strat.keys():
            # Facts should be a distribution
            if not isclose(sum(strat[issue].values()), 1):
                return False
            for value, prob in strat[issue].items():
                if not 0 <= prob <= 1:
                    return False
                if not value in self.issues[issue]:
                    return False
        return True

    def isOfferValid(self, offer):
       for issue in offer.keys():
            if not isclose(sum(offer[issue].values()), 1):
                if self.verbose >= 3:
                    print("Failed sum in issue {}!".format(issue))
                return False
            for value, prob in offer[issue].items():
                if not (isclose(prob, 1) or isclose(prob, 0)):
                    if self.verbose >= 3:
                        print("Failed value in issue {}!".format(issue))
                    return False
                if not value in self.issues[issue]:
                    if self.verbose >= 3:
                        print("Failed, unkown fact in issue {}!".format(issue))
                    return False
       return True

    def setStrat(self, strat):
        self.generateDecisionFacts()
        if not self.isStratValid(strat):
            raise ValueError("Invalid strat: {}".format(strat))

        self.stratDict = strat

    def setUtilities(self, utilities):
        self.utilities = utilities
        if self.verbose >= 3:
            print("{}'s utilities: {}".format(self.agentName,self.utilities))

    def generateDecisionFacts(self):
        self.decisionFacts = []
        for issue in self.issues.keys():
            factList = []
            for value in self.issues[issue]:
                if "." in str(value):
                    factList.append("'{issue}_{value}'".format(
                        issue=issue, value=value))
                else:
                    factList.append("{issue}_{value}".format(
                        issue=issue, value=value))
            self.decisionFacts.append(factList)

    def initUniformStrategy(self):
        for issue in self.issues.keys():
            if not issue in self.stratDict.keys():
                self.stratDict[issue] = {}
            for val in self.issues[issue]:
                self.stratDict[issue][str(val)] = 1/len(self.issues[issue])


    def compileProblogModel(self, offer):
        decisionFactsString = self.formatProblogStrat(offer)
        queryString = self.formatQueryString()
        kbString = "\n".join(self.KB) + "\n"
        return decisionFactsString + kbString + queryString


    def calcOfferUtility(self, offer):
        if not offer:
            return self.nonAgreementCost
        if not self.isOfferValid(offer):
            raise ValueError("Invalid offer received")
        problogModel = self.compileProblogModel(offer)
        if self.verbose >= 4:
            print(problogModel)
        probabilityOfFacts = self.non_leaky_problog(problogModel)
            #get_evaluatable().create_from(PrologString(problogModel)).evaluate()
        # probabilityOfFacts = {str(u): r for u, r in probabilityOfFacts.items()}

        score = 0
        for fact, reward in self.utilities.items():
            if fact in probabilityOfFacts.keys():
                score += reward * probabilityOfFacts[fact]
        if self.verbose >= 2:
            print("{}: offer is worth {}".format(self.agentName, score))
        # self.utilityCache[frozenOffer] = score
        return score

    def calcStratUtility(self, strat):
        if not self.isStratValid(strat):
            raise ValueError("Invalid strat detected: {}".format(strat))
        problogModel = self.compileProblogModel(strat)
        probabilityOfFacts = self.non_leaky_problog(problogModel)
            #get_evaluatable().create_from(PrologString(problogModel)).evaluate()
        # probabilityOfFacts = {str(u): r for u, r in probabilityOfFacts.items()}

        score = 0
        for fact, reward in self.utilities.items():
            score += reward * probabilityOfFacts[fact]

        return score


    def non_leaky_problog(self,model):
        # using the python implementation of problog causes memory leaks
        # so we use the commandline interface seperately to avoid this as a temp fix
        modelPath = abspath(join(dirname(__file__), 'models/temp_model_{}.pl'.format(getpid())))
        with open(modelPath, "w") as temp_file:
            temp_file.write(model)

        process = sp.Popen(["problog", modelPath], stdout=sp.PIPE)
        output, error = process.communicate()

        ans = {}

        for string in output.decode("ascii").split("\n"):
            if string:
                key, prob = string.strip().split(":\t")
                ans[key] = float(prob)

        remove(modelPath)

        return ans



    def accepts(self, offer):
        if self.verbose >= 2:
            print("{}: considering \n{}".format(
                self.agentName, self.formatOffer(offer)))

        if not offer:
            return False

        if type(offer) == Message:
            util = self.calcOfferUtility(offer.offer)
        else:
            util = self.calcOfferUtility(offer)

        if self.verbose >= 2:
            if util >= self.reservationValue:
                print("{}: offer is acceptable\n".format(self.agentName))
            else:
                print("{}: offer is not acceptable\n".format(self.agentName))
        return util >= self.reservationValue

    def formatProblogStrat(self, stratDict):
        returnString = ""
        for issue in stratDict.keys():
            atomList = []
            for value in stratDict[issue].keys():
                if "." in str(value):
                    atomList.append("{prob}::'{issue}_{val}'".format(
                        issue=issue, val=value, prob=stratDict[issue][value]))
                else:
                    atomList.append("{prob}::{issue}_{val}".format(
                        issue=issue, val=value, prob=stratDict[issue][value]))

            returnString += ";".join(atomList) + ".\n"

        return returnString

    def addUtilities(self, newUtils):
        self.utilities = {
            **self.utilities,
            **newUtils
        }

    def formatQueryString(self):
        queryString = ""

        for utilFact in self.utilities.keys():
            # we shouldn't ask problog for facts that we currently have no rules for
            # like we might not have after new issues are set so we'll skip those
            if any([utilFact in rule for rule in self.KB]) or any([utilFact in atom for atom in self.nestedDictToAtomDict(self.stratDict).keys()]):
                queryString += "query({utilFact}).\n".format(utilFact=utilFact)

        return queryString


    def generateOfferMessage(self):
        offer = self.generateOffer()
        if not offer:
            terminationMessage = Message(self.agentName, self.opponent.agentName,"terminate",None)
            self.recordMessage(terminationMessage)
            return terminationMessage
        # generate Offer can return a termination message if no acceptable offer can be found so we whould check for that
        if type(offer) == dict:
            return Message(self.agentName, self.opponent.agentName, kind="offer", offer=offer)
        elif type(offer) == Message:
            return offer


    def generateOffer(self):
        listedStrat = {}
        for issue in self.stratDict.keys():
            listedStrat[issue] = list(map(list, zip(*self.stratDict[issue].items())))

        for _ in range(self.maxGenerationTries):
            self.totalOffersGenerated += 1
            offer = {}
            for issue in self.stratDict.keys():
                # convert from dict to two lists so we can use np.random.choice
                # values, probs = list(map(list, zip(*self.stratDict[issue].items())))
                chosenValue = str(choice(listedStrat[issue][0], 1, p=listedStrat[issue][1])[0])
                offer[issue] = {key:0 for key in self.stratDict[issue].keys()}
                offer[issue][chosenValue] = 1
            if self.accepts(offer):
                return offer

        # we can't find a solution we can accept so just give up
        return None


    def atomDictToNestedDict(self, atomDict):
        nestedDict = {}
        for atom in atomDict.keys():
            # following pater is guarenteed to work since no _ in the names are allowed
            s = search("(.*)_(.*)", atom)
            if not s:
                raise ValueError(
                    "Coult not parse atom: {atom}".format(atom=atom))

            issue, value = s.group(1, 2)
            # atoms containing floats have an extra ' which we need to remove
            issue = sub("'", "", issue)
            value = sub("'", "", value)
            if issue not in nestedDict.keys():
                nestedDict[issue] = {}

            nestedDict[issue][value] = float(atomDict[atom])

        for issue in self.stratDict.keys():
            for value in self.stratDict[issue].keys():
                if not value in nestedDict[issue].keys():
                    nestedDict[issue][value] = 0.0


        return nestedDict

    def nestedDictToAtomDict(self, nestedDict):
        atomDict = {}
        for issue in nestedDict.keys():
            for value in nestedDict[issue].keys():
                if "." in str(value):
                    atomDict["'{issue}_{val}'".format(
                        issue=issue, val=value)] = nestedDict[issue][value]
                else:
                    atomDict["{issue}_{val}".format(
                        issue=issue, val=value)] = nestedDict[issue][value]

        return atomDict

    def formatOffer(self, offer, indentLevel=1):
        if type(offer) == Message:
            offer = offer.offer
        string = ""
        if not offer:
            return string
        for issue in offer.keys():
            string += " " * indentLevel * 4 + '{}: '.format(issue)
            for key in offer[issue].keys():
                if offer[issue][key] == 1:
                    string += "{}\n".format(key)
                    break
        return string[:-1]  # remove trailing newline
