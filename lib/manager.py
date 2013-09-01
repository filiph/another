import os
import pickle
import sqlite3
from lib.population import *

class Manager:
    """ Class manages the evolution, tracks state of the population, etc. """
    def __init__(self, size=20, crossover_probability=0.7, shared_fitness_sigma=0.05,
                 shared_fitness_alpha=1, mutation_rate=0.05, min_votes=10, directory=os.getcwd()):
        self.pop = None
        self.pop_size = size
        self.crossover_probability = crossover_probability
        self.shared_fitness_sigma = shared_fitness_sigma
        self.shared_fitness_alpha = shared_fitness_alpha
        self.mutation_rate = mutation_rate
        self.min_votes = min_votes

        self.nn_train_set = []  # Set of past phenotype performance for neural network training.

        self.directory = directory

        self.current_phenotype = None

    def start(self):
        """ Starts or re-starts population from scratch. """
        self.pop = Population(size=self.pop_size, crossover_probability=self.crossover_probability,
                              shared_fitness_sigma=self.shared_fitness_sigma,
                              shared_fitness_alpha=self.shared_fitness_alpha,
                              mutation_rate=self.mutation_rate, min_votes=self.min_votes)
        self.pop.create_first_generation()

    def close(self):
        pass

    _DEFAULT_SAVE_FILE_NAME = "manager_state.dump"

    def save(self, path=None):
        if path is None:
            path = os.path.join(self.directory, Manager._DEFAULT_SAVE_FILE_NAME)
        try:
            with open(path, "wb") as f:
                pickle.dump(self.__dict__, f)
        except IOError:
            print("ERROR: Couldn't write state to file {}.".format(path))
            raise

    def load(self, path=None):
        if path is None:
            path = os.path.join(self.directory, Manager._DEFAULT_SAVE_FILE_NAME)
        try:
            with open(path, "rb") as f:
                tmp_dict = pickle.load(f)
        except IOError:
            print("ERROR: Save file {} not found.".format(path))
            raise

        self.__dict__.update(tmp_dict)


    def step(self):
        """
        Check for new events in the evolution. Returns the list of phenotypes in the
        new generation if there is a new generation, or None if there isn't.
        """
        if self.pop.is_ready_for_next_generation():
            new_generation = self._breed_next_generation()
            return new_generation
        else:
            return None

    def _breed_next_generation(self):
        # for ph in self.pop.get_current_generation():
        #     nn_pattern_input = []
        #     for gene in ph.all_genes:
        #         nn_pattern_input.append(gene.as_int)
        #     nn_pattern_output = [ph.get_fitness_from_votes()]
        #     nn_pattern = [nn_pattern_input, nn_pattern_output]
        #     print(nn_pattern)
        #     self.nn_train_set.append(nn_pattern)

        print("TEST     : Creating new generation ({0})".format(self.pop.current_generation + 1))
        new_generation = self.pop.create_new_generation()
        # TODO: involve neural network in selecting from children
        return new_generation

# TODO: train neural network in another process
# TODO: update neural network nodes setup from the other process's results
