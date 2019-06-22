
class BooleanIssue():
    def __init__(self, name):
        self.values = [True, False]
        self.name = name
        self.is_ordinal = False
        self.is_numeric = False

    def __repr__(self):
        return str(self.name)


class NumericIssue():
    def __init__(self, name, values, is_sparse):
        self.values = sorted(values)
        self.name = name
        self.is_ordinal = True
        self.is_numeric = True
        self.is_sparse = is_sparse
