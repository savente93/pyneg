"""
A very simple deterministic negotiation agent which just enumerates \
offers in order of preference. Uses breath first search.
see :class:`EnumGenerator` for more information.
"""

from copy import deepcopy
from queue import PriorityQueue
from typing import Dict, List, Set, Tuple, cast, Optional
from uuid import uuid4

from pyneg.comms import Offer, AtomicConstraint
from pyneg.engine.evaluator import Evaluator
from pyneg.engine.generator import Generator
from pyneg.types import AtomicDict, NegSpace, NestedDict
from pyneg.utils import nested_dict_from_atom_dict


class EnumGenerator(Generator):
    """
    A simple deterministic offer generator that lists
    offers in order of preference. This implemantation
    only works for linear additive spaces and utilty functions.
    It uses breath first search to explore the negotiation space.
    Raises `StopIteration` exception when it cannot find any
    new acceptable offers.

    """
    def __init__(self, neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 acceptability_threshold: float) -> None:
        super().__init__()
        self.sorted_utils: Dict[str, List[str]] = {}
        self.neg_space = {issue: list(map(str, values))
                          for issue, values in neg_space.items()}
        self.utilities = utilities
        self.evaluator = evaluator
        self.acceptability_threshold = acceptability_threshold
        self.assignement_frontier: PriorityQueue = PriorityQueue()
        self.offer_counter: int = 0
        self.generated_offers: Set[Offer] = set()
        self.init_generator()

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

        self.evaluator.add_utilities(new_utils)
        self.init_generator()
        return True

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils
        self.evaluator.set_utilities(new_utils)
        self.init_generator()
        return True

    def init_generator(self) -> None:
        """
        Setup for the breath first search. This is done by
        indexing the negotiation space internally by utility
        e.g.
        >>> neg_space = {"boolean":["True", "False"]}
        the utility function {"boolean_True":10,"boolean_False":100} would be converted to
        {"boolean": ["False","True"]}
        """
        self.assignement_frontier = PriorityQueue()
        nested_utils = nested_dict_from_atom_dict(self.utilities)

        # Setup a grid of assignments and their utilities so
        # we can explore them later
        for issue in self.neg_space:
            if issue not in nested_utils.keys():
                nested_utils[issue] = {value:0.0 for value in self.neg_space[issue]}
                continue
            for value in self.neg_space[issue]:
                if value not in nested_utils[issue].keys():
                    nested_utils[issue][value] = 0.0

        # function to sort a list of tuples according to the second tuple field
        # in decreasing order so we can quickly identify candidates for the next offer

        def sorter(issue: str) -> List[Tuple[str, int]]:
            return cast(List[Tuple[str, int]],
                        sorted(
                            nested_utils[issue].items(),
                            reverse=True,
                            key=lambda tup: tup[1]))

        # Create dictionary of lists of value assignments by issue sorted
        # by utility in dec order
        # example: {"boolean_True":10,"boolean_False":100} => {"boolean": ["False","True"]}

        self.sorted_utils = {
            issue:
            list(map(
                lambda tup: tup[0],
                sorter(issue)))
            for issue in nested_utils}

        # Now we can find offers by simply incrementig the indices
        # for this list and looking up the corresponding values
        best_offer_indices = {issue: 0 for issue in self.neg_space}
        self.offer_counter = 0
        self.generated_offers = set()

        offer = self._offer_from_index_dict(best_offer_indices)
        if self.accepts(offer):
            util = self.evaluator.calc_offer_utility(offer)
            # index by -util to get a max priority queue instead of the standard min
            # use offer_counter to break ties
            self.assignement_frontier.put(
                (-util, self.offer_counter, best_offer_indices))
            self.generated_offers.add(
                self._offer_from_index_dict(best_offer_indices))
            self.active = True

    def accepts(self, offer: Offer) -> bool:
        """
        Determine whether the offer is acceptble according to
        the known criteria.

        :param offer: The offer to be checked
        :type offer: Offer
        :return: True iff the offer is acceptable according to the criteria.
        :rtype: bool
        """
        util = self.evaluator.calc_offer_utility(offer)
        return util >= self.acceptability_threshold

    def _expand_assignment(self, sorted_offer_indices: Dict[str, int]) -> None:
        """
        Takes a typle of offer indices and generates new valid offer
        indices from them, to be used in offer generation, and
        puts them on the fronteir. For example assume there are three
        issues with each three values, and each assignement
        has utility equal to the values. i.e.

        >>> neg_space = {"A":[1,2,3],"B":[4,5,6],"C":[7,8,9]}

        and [A->1,B->4,C->7] would have utility 1+4+7 = 12
        then

        >>> expand_assignment((2,1,1))

        would generate {(2,1,2),(2,2,2),(0,2,2)} and put them
        in the fronteir. Note that the indices (i.e. the 2,1,1)
        don't correspond to the indices in the negotiation space
        but to the indices of the internal list of values sorted
        by utility. See :func:`init_generator` for more info.

        :param sorted_offer_indices: a tuple of indices corresponding to entries \
        in the internal list refering to vaues
        :type sorted_offer_indices: Tuple[int]
        """
        for issue in self.neg_space.keys():
            copied_offer_indices = deepcopy(sorted_offer_indices)
            if copied_offer_indices[issue] + 1 >= len(self.sorted_utils[issue]):
                continue
            copied_offer_indices[issue] += 1
            offer = self._offer_from_index_dict(copied_offer_indices)
            util = self.evaluator.calc_offer_utility(offer)
            if util >= self.acceptability_threshold and self._offer_from_index_dict(
                    copied_offer_indices) not in self.generated_offers:
                self.assignement_frontier.put(
                    (-util, str(uuid4())[-8:], copied_offer_indices))
                self.generated_offers.add(
                    self._offer_from_index_dict(copied_offer_indices))

    def generate_offer(self) -> Offer:
        """
        Generates offer in breath first manner. Most of the work is done in
        :func:`init_generator`,
        :func:`expand_assignement` and
        :func:`_offer_from_index_dict`
        this function just takes the next offer from the priorityQueue and converts
        it into an offer.

        :raises StopIteration: Raised when no acceptable offers can be found.\
        in this case this is the case if we find offers that have utility \
        below acceptance threshold because we use BFS.
        :return: The next best offer with the current knowledge base.
        :rtype: Offer
        """
        if self.assignement_frontier.empty():
            self.active = False
            raise StopIteration()

        self.offer_counter += 1

        # the second index is just to ensure stable ordering in the priorityQueue
        negative_util, _, indices = self.assignement_frontier.get()
        if -negative_util <= self.acceptability_threshold:
            self.active = False
            raise StopIteration()

        self._expand_assignment(indices)
        return self._offer_from_index_dict(indices)

    def _offer_from_index_dict(self, index_dict: Dict[str, int]) -> Offer:
        """
        converts indicies corresponding to the internal list of values
        into actuall offers. e.g. assume we have

        >>> neg_space = {"A":["first","second","third"],"B":["fourth","fifth","sixth"]
        ,"C":["seventh","eighth","ninth"]}
        and each assignement has utility equal to the values. i.e.
        [A->"first",B->"forth",C->"seventh"] would have utility 1+4+7 = 12 then
        we would have

        >>> _offer_from_index_dict({"A":2,"C":0,"B":1}).get_sparse_str_repr()
        [A->"first",B->"fifth", C->"ninth"]

        :param index_dict: The dictionarry mapping issues to the corresponding \
        index in the internal list
        :type index_dict: Dict[str, int]
        :return: An offer with the mapping corresponding to the indices passed in
        :rtype: Offer
        """
        offer: NestedDict = {}
        for issue in index_dict.keys():
            offer[issue] = {}
            chosen_value: str = self.sorted_utils[issue][index_dict[issue]]
            for value in self.neg_space[issue]:
                if value == chosen_value:
                    offer[issue][value] = 1
                else:
                    offer[issue][value] = 0

        return Offer(offer)

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        print("""WARNING: attempting to use a constraint mechanism
            with non constraint aware system.
            add_constraint called in {self.class.__name__}""")
        return True

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                add_constraints called in {self.class.__name__}""")
        return True

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                find_violated_constraint called in {self.class.__name__}""")
        return None

    def get_constraints(self) -> Set[AtomicConstraint]:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                function get_constraints called in {self.class.__name__}""")
        return set()

    def get_unconstrained_values_by_issue(self, issue: str) -> Set[str]:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                get_unconstrained_values_by_issue called in {self.class.__name__}""")
        return set(self.neg_space[issue])
