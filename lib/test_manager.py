import os
from unittest import TestCase
from lib.manager import Manager

__author__ = 'Filip Hracek'


class TestManager(TestCase):
    def test_save_load_options(self):
        m1 = Manager(size=13, mutation_rate=0.013)
        m1.save()
        m1.close()

        m2 = Manager()
        m2.load()
        self.assertEqual(m2.pop_size, m1.pop_size)
        self.assertEqual(m2.mutation_rate, m1.mutation_rate)
        m2.close()

    def test_save_load_phenotypes(self):
        m = Manager()
        m.start()
        phenotypes = list(m.pop.phenotypes)
        m.save()
        m.close()

        m2 = Manager()
        m2.load()
        self.maxDiff=None
        self.assertListEqual(m2.pop.phenotypes, phenotypes)
        m2.close()

    def tearDown(self):
        try:
            os.remove(Manager._DEFAULT_PATH_TO_SAVE_FILE)
        except OSError:
            pass
