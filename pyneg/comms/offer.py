"""
Defines the Offer class.
"""
from typing import Dict, Union, cast, List, Iterable, Tuple, FrozenSet

from numpy import isclose

from pyneg.types import NestedDict, AtomicDict
from pyneg.utils import nested_dict_from_atom_dict, atom_from_issue_value


class Offer:
    """
    This essentially is a function from all of
    the issue value pairs to {0.0,1.0}. Can be repesended as a
    NestedDict or an AtomicDict. The assignements should be binary
    and the sum of all assignements for an issue should sum to 1.0
    (i.e. exactly one value should be assigned 1.0 and all others 0.0).
    Note that the assignements should be floats instead of ints or bools.
    this is for compatibility with ProbLog.

    e.g.
    >>> nested = {"First": {"A":0.0, "B":1.0}, "Second":{"C":1.0,"D":0.0}}
    >>> atomic = {"First_A":0.0, "First_B":1.0, "Second_C":1.0, "Second_D":0.0}

    """
    def __init__(self, values_by_issue: Union[NestedDict, AtomicDict],
                 indent_level: int = 1):
        self.indent_level = indent_level
        if not isinstance(values_by_issue, dict):
            raise TypeError(
                "Expected a dictionary not {}".format(type(values_by_issue)))

        # is it a nested dictionary?
        if isinstance(next(iter(values_by_issue.values())), dict):
            self.values_by_issue: NestedDict = cast(
                NestedDict, values_by_issue)

        # is it an Atomic dictionary?
        elif isinstance(next(iter(values_by_issue.values())), float):
            # convert to nested dict so checking for validity is easier
            self.values_by_issue = nested_dict_from_atom_dict(
                values_by_issue)
        else:
            raise ValueError(
                "invalid offer structure: {}".format(values_by_issue))

        # check offer contents are valid
        for issue in self.values_by_issue.keys():
            if not isclose(sum(self.values_by_issue[issue].values()), 1):
                raise ValueError(
                    f"Invalid offer, {issue} doesn't sum to 1 in dict {self.values_by_issue}")
            for value, prob in self.values_by_issue[issue].items():
                if not (isclose(prob, 1) or isclose(prob, 0)):
                    raise ValueError(
                        f"Invalid offer, {issue} has non-binary assignement")
                if value not in self.values_by_issue[issue].keys():
                    raise ValueError(
                        f"Invalid offer, {issue} has unknown value: {value}")

        for issue in self.values_by_issue.keys():
            for value in self.values_by_issue[issue].keys():
                if not isinstance(self.values_by_issue[issue][value], float):
                    self.values_by_issue[issue][value] = float(
                        self.values_by_issue[issue][value])

    # will return the one value which is assigned 1
    # there is guaranteed to be exactly one value with a
    # non zero choice
    def get_chosen_value(self, issue: str) -> str:
        """
        Each issue has exactly one value that it "chooses" i.e. has assigned 1 to.
        This one returns that value.

        :param issue: The issue of which you want to get the chosen value.
        :type issue: str
        :raises RuntimeError: raises when no choice is made
        :return: the value chosen by the offer.
        :rtype: str
        """
        for val in self.values_by_issue[issue]:
            if isclose(self.values_by_issue[issue][val], 1):
                return val

        raise RuntimeError("invalid internal offer state.")

    def __getitem__(self, key: str) -> Dict[str, float]:
        return self.values_by_issue[key]

    def is_assigned(self, issue: str, value: str) -> bool:
        """
        Checks whether the passed issue value pair is the
        one chosen by this offer

        :param issue: The issue to check
        :type issue: str
        :param value: The value to check
        :type value: str
        :return: True iff this offer poposes the asssignement of `value` to `issue`
        :rtype: bool
        """
        return cast(bool, isclose(self.values_by_issue[issue][value], 1))

    def get_issues(self) -> Iterable[str]:
        """
        Returns all issues associated with this offer

        :return: an iterable containting the issues associated with this offer
        :rtype: Iterable[str]
        """
        return self.values_by_issue.keys()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Offer):
            return False

        # This way sparse and dense offers can still be equal
        # but they must have the same issues
        for issue in self.values_by_issue.keys():
            my_chosen_value = self.get_chosen_value(issue)
            their_chosen_value = other.get_chosen_value(issue)
            if my_chosen_value != their_chosen_value:
                return False

        return True

    def __repr__(self) -> str:
        return self.get_sparse_str_repr()

    def get_problog_dists(self) -> str:
        """
        Formats the offer as a distribution over the
        atomic issue value pairs. This is just so
        ProbLog agents can reason about them.

        >>> Offer(atomic).get_problog_dists()
        0.0::First_A;1.0::First_B.
        1.0::Second_C;0.0::Second_D.


        :return: A string expressing the offer in valid ProbLog as \
        a distribution over the atomic issue value pairs.
        :rtype: str
        """
        return_string = ""
        for issue in self.values_by_issue.keys():
            atom_list: List[str] = []
            for value in self.values_by_issue[issue].keys():
                atom = atom_from_issue_value(
                    issue, value)
                atom_list.append("{prob}::{atom}".format(
                    prob=self.values_by_issue[issue][value], atom=atom))

            return_string += ";".join(atom_list) + ".\n"

        return return_string

    def get_sparse_repr(self) -> FrozenSet[Tuple[str, str]]:
        """
        returns a sparse reperesentation of itself. This means a frozenset of
        issue value pairs, where the value is the one assigned byt the offer.
        Handy for logging and hashing

        >>> Offer(atomic).get_sparse_repr()
        frozenset({('First', 'B'), ('Second', 'C')})

        :return: A frozen set containt assigned issue value pairs
        :rtype: FrozenSet[Tuple[str,str]]
        """
        return frozenset({(issue, self.get_chosen_value(issue))
                          for issue in self.values_by_issue.keys()})

    def get_sparse_str_repr(self) -> str:
        """
        returns a sparse string reperesentation of itself. Mainly useful for logging

        >>> Offer(atomic).get_sparse_str_repr()
        [First->B, Second->C]

        :return: A string of the mapping
        :rtype: str
        """
        return "[" \
            + ", ".join([f"{issue}->{self.get_chosen_value(issue)}" for
                         issue in self.values_by_issue.keys()]) \
            + "]"

    def __hash__(self):
        return hash(self.get_sparse_repr())
