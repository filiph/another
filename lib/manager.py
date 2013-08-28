import sqlite3
from lib.population import *

PATH_TO_SCRIPT = os.path.dirname(os.path.realpath(__file__))
PATH_TO_POP_DUMP = PATH_TO_SCRIPT + "/population.dump"

class Manager:
    """ Class manages the evolution, tracks state of the population, etc. """
    def __init__(self, pop):
        if pop == None:
            self.pop = Population()
        else:
            self.pop = pop

        nn_train_set = []  # Set of past phenotype performance for neural network training.

    def save_pop_to_file(self):
        print("Trying to save population...")
        try:
            with open(PATH_TO_POP_DUMP, "wb") as f:
                pickle.dump(self.pop, f)
                print("Population saved to " + PATH_TO_POP_DUMP)
        except IOError:
            print("ERROR: Couldn't write population to file.")
            raise

    def start(self):
        """ Starts or re-starts population from scratch. """
        self.pop.create_first_generation()

    def step(self):
        if self.pop.is_ready_for_next_generation():
            self.breed_next_generation()

    def breed_next_generation(self):
        for ph in self.pop.get_current_generation():
            nn_pattern_input = []
            for gene in ph.all_genes:
                nn_pattern_input.append(gene.get_int())
            nn_pattern_output = [ph.get_fitness_from_votes()]
            nn_pattern = [nn_pattern_input, nn_pattern_output]
            print(nn_pattern)
            nn_train_set.append(nn_pattern)

        gen_desirabilities.append(get_current_generation_desirability(pop))
        gen_avg_desirabilities.append(get_current_generation_average_desirability(pop))
        best_desirabilities.append(get_best_desirability(pop))
        print("TEST     : Creating new generation ({0})".format(pop.current_generation + 1))
        children = pop.create_new_generation()

