from unittest import TestCase
from pyneg.utils import neg_scenario_from_util_matrices, nested_dict_from_atom_dict
from pyneg.engine import EnumGenerator, LinearEvaluator
from pyneg.comms import Offer
from numpy import arange


class TestStrategy(TestCase):

    def setUp(self):
        raise NotImplementedError()

    def test_trival(self):
        pass
