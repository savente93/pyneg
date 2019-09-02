from unittest import TestCase


class TestRandomGenerator(TestCase):

    def setUp(self):
        raise NotImplementedError()

    def test_trival(self):
        pass

    # def test_doesnt_generate_same_offer_five_times(self):
    #     # since some elements might be randomly picked it can sometimes happen that the elements are the same but it
    #     # shouldn't keep happening so we'll try it a couple of times
    # last_offer = self.generator.generate_offer()
    # for _ in range(5):
    #     new_offer = self.generator.generate_offer()
    #     self.assertNotEqual(last_offer, new_offer)
    #     last_offer = new_offer
