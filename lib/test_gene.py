from unittest import TestCase
from lib.gene import Gene

__author__ = 'filiph'

class TestGene(TestCase):
    # def test_set_from_string(self):
    #     self.fail()
    #
    # def test_set_from_mating(self):
    #     self.fail()
    #
    # def test_set_from_int(self):
    #     self.fail()

    def test_get_bool(self):
        g = Gene(0, 1)
        g.set_from_string("1")
        self.assertEqual(g.get_bool(), True)
        g.set_from_string("0")
        self.assertEqual(g.get_bool(), False)
        g = Gene(0, 2)
        g.set_from_string("01")
        self.assertRaises(AssertionError, g.get_bool)

    # def test_get_int(self):
    #     self.fail()
    #
    # def test_get_max_int(self):
    #     self.fail()
    #
    # def test_get_binary_string(self):
    #     self.fail()
    #
    # def test_check_initialized(self):
    #     self.fail()
    #
    # def test_get_relative_value(self):
    #     self.fail()
    #
    # def test_randomize(self):
    #     self.fail()