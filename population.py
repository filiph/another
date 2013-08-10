import random

from phenotype import Phenotype

class Population:
    def __init__(self):
        self.phenotypes = []
        self.current = None
        self.current_generation = -1

    def create_first_generation(self, size):
        for i in range(0, size):
            ph = Phenotype(i)
            ph.generation = 0
            ph.randomize()
            self.phenotypes.append(ph)
        self.current_generation = 0
        self.current = self.phenotypes[0]

    def get_next(self, check_callback=None):
        """ Returns the next phenotype to be shown. """
        assert(len(self.phenotypes) > 0)
        candidate = None
        while True:
            candidate = self.get_random()
            if (candidate is not self.current):
                if (check_callback != None and check_callback(candidate)):
                    break
        self.current = candidate
        return candidate

    def get_random(self):
        # TODO: currently living have much higher chance to be picked
        # TODO: non-resolved (insignificant numbers) have higher chance
        return random.choice(self.get_current_generation())

    def get_current_generation(self):
        def current(ph): return ph.generation == self.current_generation
        return list(filter(current, self.phenotypes))

# pop = Population()
# pop.create_first_generation(5)
# print(pop.phenotypes)
