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

    def test_int_saves_and_loads(self):
        MAX_BITS = 8
        for bit_length in range(1, MAX_BITS):
            g = Gene(0, bit_length)
            for integer in range(2 ** bit_length):
                g.as_int = integer
                self.assertEqual(g.as_int, integer)

    def test_get_bool(self):
        g = Gene(0, 1)
        g.as_string = "1"
        self.assertEqual(g.as_bool, True)
        g.as_string = "0"
        self.assertEqual(g.as_bool, False)
        g = Gene(0, 2)
        g.as_string = "01"
        self.assertRaises(AssertionError, lambda: g.as_bool)

    def test_set_bool(self):
        g = Gene(0, 1)
        g.as_bool = True
        self.assertEqual(g.as_bool, True)
        g.as_bool = False
        self.assertEqual(g.as_bool, False)

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