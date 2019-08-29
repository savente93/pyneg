from unittest import TestCase


class TestStrategy(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        raise NotImplementedError()
