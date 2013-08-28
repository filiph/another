import sqlite3
from lib.population import *

class Manager:
    """ Class manages the evolution, tracks state of the population, etc. """
    def __init__(self):
        self.pop = None

        self.nn_train_set = []  # Set of past phenotype performance for neural network training.

    def start(self):
        """ Starts or re-starts population from scratch. """
        self.pop = Population()
        self.pop.create_first_generation()

    def load_state(self, path):
        pass  # load state from an sqlite (?) file

    def step(self):
        """
        Check for new events in the evolution. Returns the list of phenotypes in the
        new generation if there is a new generation, or None if there isn't.
        """
        if self.pop.is_ready_for_next_generation():
            new_generation = self.breed_next_generation()
            return new_generation
        else:
            return None

    def breed_next_generation(self):
        for ph in self.pop.get_current_generation():
            nn_pattern_input = []
            for gene in ph.all_genes:
                nn_pattern_input.append(gene.get_int())
            nn_pattern_output = [ph.get_fitness_from_votes()]
            nn_pattern = [nn_pattern_input, nn_pattern_output]
            print(nn_pattern)
            self.nn_train_set.append(nn_pattern)

        print("TEST     : Creating new generation ({0})".format(self.pop.current_generation + 1))
        new_generation = self.pop.create_new_generation()
        # TODO: involve neural network in selecting from children
        return new_generation

# TODO: train neural network in another process
# TODO: update neural network nodes setup from the other process's results