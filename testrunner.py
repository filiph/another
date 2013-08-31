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

index = 0
for size in [10, 20, 30, 50, 70, 100]:
    for crossover_probability in [0.0, 0.5, 0.7, 0.9, 1.0]:
        for shared_fitness_sigma in [0.0, 0.02, 0.05, 0.10, 0.20]:
            for mutation_rate in [0.0, 0.05, 0.1, 0.2]:
                for min_votes in [10, 20, 50]:
                    tries = 2
                    improvement_results = []
                    for i in range(tries):
                        m = Manager(size=size, crossover_probability=crossover_probability,
                                    shared_fitness_sigma=shared_fitness_sigma,
                                    mutation_rate=mutation_rate, min_votes=min_votes)
                        m.start()
                        runner = Runner(m, objective_function=get_desirability)
                        runner.run(1000)
                        improvement = runner.improvement
                        improvement_results.append(improvement)
                    mean, variance = compensated_mean_and_variance(improvement_results)
                    index += 1
                    str_list.append("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
                        index, size, crossover_probability, shared_fitness_sigma, mutation_rate,
                        min_votes, mean, variance
                    ))
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

