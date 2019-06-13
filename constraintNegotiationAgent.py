from randomNegotiationAgent import RandomNegotiationAgent
from message import Message
from constraint import Constraint, AtomicConstraint
from pandas import Series
from time import time
from os.path import abspath, dirname, join
from re import search,sub

class ConstraintNegotiationAgent(RandomNegotiationAgent):
    def __init__(self,uuid, utilities, kb, reservationValue, nonAgreementCost, issues=None,constraintThreshold= -20, maxRounds=10000, verbose=0, name="", reporting=False, meanUtility=0,stdUtility=0):
        super().__init__(uuid,utilities, kb, reservationValue,
                         nonAgreementCost, issues=issues, verbose=verbose,reporting=reporting,meanUtility=meanUtility,stdUtility=stdUtility)
        self.negotiationActive = False
        self.agentName = name
        self.successful = False
        self.stratName = "Constrained"
        self.messageCount = 0
        self.maxRounds = maxRounds
        self.ownConstraints = set()
        self.opponentConstraints = set()
        self.constraintsSatisfiable = True
        self.constraintThreshold = constraintThreshold

    def addUtilities(self, newUtils):
        for atom,util in newUtils.items():
           self.utilities[atom] = util
           if util <= self.constraintThreshold:
               s = search("(.*)_(.*)", atom)
               if not s:
                   raise ValueError(
                       "Coult not parse atom: {atom}".format(atom=atom))

               issue, value = s.group(1, 2)
               issue = sub("'", "", issue)
               value = sub("'", "", value)
               constraint = AtomicConstraint(issue,value)

               if self.verbose >= 3:
                   print("{} is adding own constraint {} because of low utility {}.".format(self.agentName,constraint,util))

               self.addOwnConstraint(constraint)



    def initUniformStrategy(self):
        # if there are no constraints we can skip all of the checks
        if not self.getAllConstraints():
            super().initUniformStrategy()
            return


        for issue in self.issues.keys():
            self.stratDict[issue] = {}
            issueConstrainedValues = [
                constr.value for constr in self.getAllConstraints() if constr.issue == issue]
            issueUnConstrainedValues = set(self.issues[issue]) - set(issueConstrainedValues)
            for val in self.issues[issue]:
                if val in issueUnConstrainedValues:
                    self.stratDict[issue][val] = 1 / len(issueUnConstrainedValues)
                else:
                    self.stratDict[issue][val] = 0.0

    def addOwnConstraint(self, constraint):
        if self.verbose >= 2:
            print("{} is adding own constraint: {}".format(
                self.agentName, constraint))

            if self.verbose >= 3:
                print("stratagy before adding constraint: {}".format(self.stratDict))
        self.ownConstraints.add(constraint)
        for issue in self.stratDict.keys():
            issueConstrainedValues = [
                constr.value for constr in self.getAllConstraints() if constr.issue == issue]
            issueUnConstrainedValues = set(
                self.stratDict[issue].keys()) - set(issueConstrainedValues)
            if len(issueUnConstrainedValues) == 0:
                if self.verbose >= 2:
                    print("Found incompatible constraint: {}".format(constraint))
                self.constraintsSatisfiable = False
                #Unsatisfyable constraint so we're terminating on the next message so we won't need to update the strat
                return


            for value in self.stratDict[issue].keys():
                if not constraint.isSatisfiedByAssignement(issue, value):
                    self.stratDict[issue][value] = 0

            # it's possible we just made the last value in the stratagy 0 so we have to figure out which value is still unconstrained
            # and set that one to 1
            if sum(self.stratDict[issue].values()) == 0:
                self.stratDict[issue][next(iter(issueUnConstrainedValues))] = 1
            else:
                stratSum = sum(self.stratDict[issue].values())
                self.stratDict[issue] = {
                    key: prob/stratSum for key, prob in self.stratDict[issue].items()}
        atom = "{issue}_{value}".format(issue=constraint.issue, value=constraint.value)
        if not atom in self.utilities.keys():
            self.utilities[atom] = self.nonAgreementCost


        if self.verbose >= 3:
            print("stratagy after adding constraint: {}".format(self.stratDict))


    def addOpponentConstraint(self, constraint):
        if self.verbose >= 2:
            print("{} is adding opponent constraint: {}".format(
                self.agentName, constraint))
        if self.verbose >= 3:
            print("stratagy before adding constraint: {}".format(self.stratDict))
        self.opponentConstraints.add(constraint)
        for issue in self.stratDict.keys():
            issueConstrainedValues = [
                constr.value for constr in self.getAllConstraints() if constr.issue == issue]
            issueUnConstrainedValues = set(
                self.stratDict[issue].keys()) - set(issueConstrainedValues)

            if len(issueUnConstrainedValues) == 0:
                if self.verbose >= 2:
                    print("Found incompatible constraint: {}".format(constraint))


                self.constraintsSatisfiable = False
                #Unsatisfyable constraint so we're terminating on the next message so we won't need to update the strat
                return
            
            for value in self.stratDict[issue].keys():
                if not constraint.isSatisfiedByAssignement(issue, value):
                    self.stratDict[issue][value] = 0

            # it's possible we just made the last value in the stratagy 0 so we have to figure out which value is still unconstrained
            # and set that one to 1
            if sum(self.stratDict[issue].values()) == 0:
                self.stratDict[issue][next(iter(issueUnConstrainedValues))] = 1
            else:
                stratSum = sum(self.stratDict[issue].values())
                self.stratDict[issue] = {
                    key: prob / stratSum for key, prob in self.stratDict[issue].items()}

        self.addUtilities(
            {"{issue}_{value}".format(issue=constraint.issue, value=constraint.value): self.nonAgreementCost})

        if self.verbose >= 3:
            print("stratagy after adding constraint: {}".format(self.stratDict))

    def satisfiesAllConstraints(self, offer):
        allConstraints = self.getAllConstraints()
        for constr in allConstraints:
            if not constr.isSatisfiedByStrat(offer):
                return False
        return True

    def generateNextMessageFromTranscript(self):
        try:
            lastMessage = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self.generateOfferMessage()

        if self.verbose >= 3:
            print("{} is using {} to generate next offer.".format(self.agentName,lastMessage))


        if lastMessage.constraint:
            if self.verbose >= 2:
                print("{} is adding opponent constraint {}".format(self.agentName,lastMessage.constraint))
            self.addOpponentConstraint(lastMessage.constraint)

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
            return Message(self.agentName, self.opponent.agentName, "terminate", None)

        if self.accepts(lastMessage.offer):
            self.negotiationActive = False
            self.successful = True
            self.report()
            return Message(self.agentName, self.opponent.agentName, "accept", lastMessage.offer)

        violatedConstraint = self.generateViolatedConstraint(lastMessage.offer)
        return self.generateOfferMessage(violatedConstraint)

    def generateOfferMessage(self,constr = None):
        offer = self.generateOffer()
        if not offer:
            self.negotiationActive = False
            self.successful = False
            terminationMessage = Message(self.agentName, self.opponent.agentName, "terminate", None)
            self.recordMessage(terminationMessage)
            self.report()
            return terminationMessage

        if not self.satisfiesAllConstraints(offer):
            raise RuntimeError("should not be able to generate constraint violating offer: {}\n constraints: {}".format(offer,self.getAllConstraints()))
            # raise RuntimeError("should not be able to generate constraint violating offer")

        if not self.isOfferValid(offer):
            if self.verbose>=3:
                raise RuntimeError("{} generated invalid offer: {}".format(self.agentName,offer))
            raise RuntimeError("{} generated invalid offer".format(self.agentName))
        # generate Offer can return a termination message if no acceptable offer can be found so we whould check for that
        if type(offer) == dict:
            return Message(self.agentName, self.opponent.agentName, kind="offer", offer=offer, constraint=constr)
        elif type(offer) == Message:
            offer.constraint = constr
            return offer

    def generateOffer(self):
        if self.constraintsSatisfiable:
            return super().generateOffer()
        else:
            raise RuntimeError("Cannot generate offer with incompatable constraints: {}".format(self.getAllConstraints()))

    def generateViolatedConstraint(self, offer):

        for constr in self.ownConstraints:
            for issue in offer.keys():
                for value in offer[issue].keys():
                    if not constr.isSatisfiedByAssignement(issue, value):
                        return AtomicConstraint(issue, value)

    def calcOfferUtility(self, offer):
        if not offer:
            return self.nonAgreementCost
        if not self.isOfferValid(offer):
            raise ValueError("Invalid offer received: {}".format((offer)))
        if not self.satisfiesAllConstraints(offer):
            return self.nonAgreementCost

        return super().calcOfferUtility(offer)

    def shouldTerminate(self, msg):
        return self.messageCount >= self.maxRounds or not self.constraintsSatisfiable


    def receiveMessage(self, msg):
        if self.verbose >= 1:
            print("{}: received message: {}".format(self.agentName, msg))
        self.recordMessage(msg)
        if msg.constraint:
            self.addOpponentConstraint(msg.constraint)
            if self.verbose >= 3:
                print("constraints still consistant: {}".format(self.constraintsSatisfiable))

    def getAllConstraints(self):
        return self.ownConstraints.copy().union(self.opponentConstraints)

    def accepts(self, offer):
        if self.verbose >= 2:
            print("{}: considering \n{}".format(
                self.agentName, self.formatOffer(offer)))

        if not offer:
            return False

        if not self.satisfiesAllConstraints(offer):
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

    def receiveNegotiationRequest(self, opponent, issues):
        # allows others to initiate negotiations with us
        # we allways accept calls for negotiation if we can init propperly and don't have incompatable constraints
        try:
            if self.constraintsSatisfiable:
                self.setupNegotiation(issues)
                self.opponent = opponent
                return True
            else:
                return False
        except:
            # something went wrong setting up so reject request
            print("{} failed to setup negotiation propperly".format(self.agentName))
            return False


    def setupNegotiation(self, issues):
        super().setupNegotiation(issues)
        if self.verbose >= 2:
            print("{}: starting constraints: {}".format(self.agentName,self.ownConstraints))

    def negotiate(self, opponent):
        if self.constraintsSatisfiable:
            return super().negotiate(opponent)
        else:
            return False


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
            log['numbOfOwnConstraints'] = len(self.ownConstraints)
            log['numbOfDiscoveredConstraints'] = len(self.opponentConstraints)
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