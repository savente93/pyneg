"""
This module defines the strategy that probabalistic
generators can use. See :class:`Strategy` for more information.
"""

from typing import Dict, List, Iterable, Union, cast

from numpy import isclose

from pyneg.types import AtomicDict, NestedDict, Verbosity
from pyneg.utils import nested_dict_from_atom_dict, atom_from_issue_value


class Strategy():
    """
    A class that probabalistic generators can use to generate
    offers by sampling. A stagy consists of a distribution
    for every issue over it's possible values.

    :raises ValueError: raised if input doesn't have the right structure \
        e.g. if some of the vectors arent a distribution
    :raises KeyError: [description]
    :return: [description]
    :rtype: [type]
    """

    def __init__(self, values_by_issue: Union[NestedDict, AtomicDict],
                 indent_level: int = 1, verbose=Verbosity.none):
        self.indent_level = indent_level
        self.verbose = verbose
        if isinstance(next(iter(values_by_issue.values())), dict):
            self.values_by_issue: NestedDict = cast(
                NestedDict, values_by_issue)
        elif isinstance(next(iter(values_by_issue.values())), float):
            # convert to nested dict so checking for validity is easier
            self.values_by_issue = nested_dict_from_atom_dict(
                values_by_issue)
        else:
            raise ValueError(f"invalid offer structure: {values_by_issue}")

        for issue in self.values_by_issue.keys():
            if not isclose(sum(self.values_by_issue[issue].values()), 1):
                raise ValueError(f"Invalid offer, {issue} doesn't sum to 1")
            for value, prob in self.values_by_issue[issue].items():
                if not 0 <= prob <= 1:
                    raise ValueError(f"Invalid offer, {issue} has non-binary assignement")
                if value not in self.values_by_issue[issue].keys():
                    raise ValueError(f"Invalid offer, {issue} has unknown value: {value}")

    def get_value_dist(self, issue: str) -> Dict[str, float]:
        """
        returns the distribution associated with the given issue.

        :param issue: The issue that you want to get the distribution for.
        :type issue: str
        :raises KeyError: if the given issue is not known.
        :return: A distribution over the values of the given issue \
            represented as a dictionary.
        :rtype: Dict[str, float]
        """
        if issue in self.values_by_issue.keys():
            return self.values_by_issue[issue]

        raise KeyError(f"Issue {issue} is not known")

    def get_issues(self) -> Iterable[str]:
        """
        returns an iterable containing all the known issues

        :return: Iterable containing all the known issues
        :rtype: Iterable[str]
        """
        return self.values_by_issue.keys()

    def set_prob(self, issue: str, value: str, prob: float) -> None:
        """
        Sets the probability of the issue issue value pair.

        :param issue: the issue to which the distribution is refering too
        :type issue: str
        :param value: the value to update the probability of
        :type value: str
        :param prob: the value to set the probability to
        :type prob: float
        """
        self.values_by_issue[issue][value] = prob

    def normalise_issue(self, issue: str) -> None:
        """
        Normalise distribution of the given issue.

        :param issue: the issue who's distribution you want to normalise
        :type issue: str
        """
        value_dist_sum = sum(self.get_value_dist(issue).values())
        self.values_by_issue[issue] = {
            key: prob / value_dist_sum for key, prob in self.values_by_issue[issue].items()}

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
