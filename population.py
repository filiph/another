
from phenotype import Phenotype

class Population:
    def __init__(self):
        self.phenotypes = []
    
    def create_first_generation(self, size):
        for i in range(0, size):
            ph = Phenotype(i)
            ph.randomize()
            self.phenotypes.append(ph)


pop = Population()
pop.create_first_generation(5)
print(pop.phenotypes)
