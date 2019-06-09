from src.constraint import Constraint


class Message():
    def __init__(self, sender, recipient, kind, offer, constraint=None):
        self.sender = sender
        self.recipient = recipient
        if kind == "empty":
            if offer:
                raise ValueError("empty message cannot have an offer")
            self.kind = "empty"
            self.offer = None
            self.constraint = None
            return

        if kind in ['accept', 'terminate', 'offer']:
            if not offer and kind != 'terminate':
                raise ValueError("Non empty message must have an offer")
            if type(offer) != dict and kind != 'terminate':
                raise ValueError(
                    "Offer should be a dict not {}".format(type(offer).__name__))
            self.kind = kind
            self.offer = offer
            self.constraint = constraint
            return

        raise ValueError("Unknown message type {}".format(kind))

    def isEmpty(self):
        return self.kind == "empty"

    def isAcceptance(self):
        return self.kind == "accept"

    def isTermination(self):
        return self.kind == "terminate"

    def hasConstraint(self):
        return not self.constraint is None

    def isOffer(self):
        return self.kind == "offer"

    def getConstraint(self):
        if not self.hasConstraint():
            raise ValueError(
                "Message does not contain constraint")

        return self.constraint

    def __hash__(self):
        return hash(self.sender, self.recipient, self.kind, self.offer, self.constraint)

    def __eq__(self, other):
        if other.__class__ != self.__class__:
            # print("unequal class")
            return False

        if other.kind != self.kind:
            # print("unequal kind")
            return False

        if other.offer != self.offer:
            # print("unequal offer")
            return False

        if other.constraint != self.constraint:
            # print("unequal constraint")
            return False

        return True

    def formatOffer(self, offer, indentLevel=1):
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

    def __repr__(self):
        # if self.kind == "empty":
        #     return "Message({sender}, {recip}, empty)".format(sender=self.sender, recip=self.recipient)

        if not self.offer:
            return "Message({sender}, {recip}, {kind})".format(sender=self.sender, recip=self.recipient, kind=self.kind)

        if self.constraint:
            return "Message({sender}, {recip}, {kind}, \n{offer}, \n{constraint}\n)".format(sender=self.sender, recip=self.recipient, kind=self.kind, offer=self.formatOffer(self.offer), constraint=self.constraint)
        else:
            return "Message({sender}, {recip}, {kind}, \n{offer}\n)".format(sender=self.sender, recip=self.recipient, kind=self.kind, offer=self.formatOffer(self.offer))
