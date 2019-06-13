import unittest


class BooleanIssue():
    def __init__(self, name):
        self.values = [True, False]
        self.name = name
        self.isOrdinal = False
        self.isNumeric = False

    def __repr__(self):
        return str(self.name)


class NumericIssue():
    def __init__(self, name, values, isSparse):
        self.values = sorted(values)
        self.name = name
        self.isOrdinal = True
        self.isNumeric = True
        self.isSparse = isSparse
