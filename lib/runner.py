__author__ = 'filiph'

import random

def default_objective_function(ph):
    """
    The default objective function considers bigger numbers as better ("1111" is better than
    "0011").
    """
    return int(ph.as_string, 2) / float(2 ** len(ph.as_string))

class Runner:
    """
    Runs a concrete setup of a simulation.
    """
    def __init__(self, manager, objective_function=default_objective_function):
        self.manager = manager
        self.objective_function = objective_function
        assert(callable(self.objective_function))

        self.gen_avg_desirabilities = []
        self.gen_best_desirabilities = []

    def run(self, iterations):
        for i in range(iterations):
            if (i % 100 == 0):
                print("RUNNER   : Iteration {0}".format(i))
            ph = random.choice(list(self.manager.pop.get_current_generation()))
            if random.random() < self.objective_function(ph):
                ph.yes += 1
            else:
                ph.no += 1

            new_generation = self.manager.step()
            if new_generation is not None:
                self.gen_avg_desirabilities.append(
                    Runner.get_average_desirability(new_generation, self.objective_function))
                self.gen_best_desirabilities.append(
                    Runner.get_best_desirability(new_generation, self.objective_function))

    def get_average_desirability(phenotypes, objective_function):
        score = 0
        for ph in phenotypes:
            score += objective_function(ph)
        return score / float(len(phenotypes))

    def get_best_desirability(phenotypes, objective_function):
        best_result = 0
        for ph in phenotypes:
            result = objective_function(ph)
            if result > best_result:
                best_result = result
        return best_result
