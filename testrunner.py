# Used to find the best evolution strategy.

import sys
import random

from lib.manager import Manager
from lib.runner import Runner

DESIRABLE_OUTCOMES = [
        "1111111111111111",
        "0000000000000000",
        "0000000010101010",
        "0000000001010101"]

def get_match(dna1, dna2):
    assert(len(dna1) == len(dna2))
    matched = 0
    for i in range(0, len(dna1)):
        if dna1[i] == dna2[i]:
            matched += 1
    return matched / float(len(dna1))

def get_desirability(ph):
    best_result = 0
    for outcome in DESIRABLE_OUTCOMES:
        result = get_match(ph.as_string, outcome)
        if result > best_result:
            best_result = result
    return best_result

# from http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Compensated_variant
def compensated_mean_and_variance(data):
    n = 0
    sum1 = 0
    for x in data:
        n = n + 1
        sum1 = sum1 + x
    mean = sum1/float(n)

    sum2 = 0
    sum3 = 0
    for x in data:
        sum2 = sum2 + (x - mean)**2
        sum3 = sum3 + (x - mean)
    variance = (sum2 - sum3**2/float(n))/float(n - 1)
    return (mean, variance)


str_list = ["#\tSize\tCrossover P\tShared Fitness Sigma\tMutation Rate\tMin "
            "Votes\tImprovement\tImprovement Variance"]

TRIES = 10
ITERATIONS = 5000

sizes = [10, 15, 20]
crossover_probabilities = [0.6, 0.7, 0.8, 0.9]
shared_fitness_sigmas = [0.05]
mutation_rates = [0.01, 0.02, 0.03, 0.05]
min_votes_tests = [20]

total_permutations = len(sizes) * len(crossover_probabilities) * len(shared_fitness_sigmas) * \
                     len(mutation_rates) * len(min_votes_tests)

index = 0
for size in sizes:
    for crossover_probability in crossover_probabilities:
        for shared_fitness_sigma in shared_fitness_sigmas:
            for mutation_rate in mutation_rates:
                for min_votes in min_votes_tests:
                    improvement_results = []
                    for i in range(TRIES):
                        m = Manager(size=size, crossover_probability=crossover_probability,
                                    shared_fitness_sigma=shared_fitness_sigma,
                                    mutation_rate=mutation_rate, min_votes=min_votes)
                        m.start()
                        runner = Runner(m, objective_function=get_desirability)
                        runner.run(ITERATIONS)
                        improvement = runner.improvement
                        improvement_results.append(improvement)
                    mean, variance = compensated_mean_and_variance(improvement_results)
                    index += 1
                    str_list.append("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6:f}\t{7:f}".format(
                        index, size, crossover_probability, shared_fitness_sigma, mutation_rate,
                        min_votes, mean, variance
                    ))
                    print("{0:.2%} - PERMUTATION {1}/{2} COMPLETE".format(index / float(
                        total_permutations), index, total_permutations))
                    print(str_list[-1])

print("== RESULTS ==")
print("\n".join(str_list))


# m = Manager(size=10)
# m.start()
# runner = Runner(m, objective_function=get_desirability)
#
# runner.run(2000)
#
# print("Runner completed with end result: {0:.0f} improvement".format(runner.improvement * 100))

