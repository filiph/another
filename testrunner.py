# Used to find the best evolution strategy.

import os
import sys
import random
import pickle

from lib.population import *
from lib.manager import Manager
from lib.neural import NN

DESIRABLEOUTCOMES = [
        "1111111111111111",
        "0000000000000000",
        "1010101010101010",
        "0101010101010101"]

ITERATIONS = 5000


def get_match(dna1, dna2):
    assert(len(dna1) == len(dna2))
    matched = 0
    for i in range(0, len(dna1)):
        if dna1[i] == dna2[i]:
            matched += 1
    return matched / float(len(dna1))

def get_desirability(ph):
    bestresult = 0
    for outcome in DESIRABLEOUTCOMES:
        result = get_match(ph.get_binary_string(), outcome)
        if result > bestresult:
            bestresult = result
    return bestresult

def get_generation_average_desirability(phenotypes):
    score = 0
    for ph in phenotypes:
        score += get_desirability(ph)
    return score / float(len(phenotypes))

def get_generation_desirability(phenotypes):
    score = 0
    for outcome in DESIRABLEOUTCOMES:
        bestresult = 0
        for ph in phenotypes:
            result = get_match(ph.get_binary_string(), outcome)
            if result > bestresult:
                bestresult = result
        score += bestresult
    return score

def get_best_desirability(pop):
    score = 0
    for outcome in DESIRABLEOUTCOMES:
        bestresult = 0
        for ph in pop.phenotypes:
            result = get_match(ph.get_binary_string(), outcome)
            if result > bestresult:
                bestresult = result
        score += bestresult
    return score


print("TEST     : Creating random sample")
m = Manager()
m.start()

gen_desirabilities = []
gen_avg_desirabilities = []
best_desirabilities = []

print("TEST     : Starting voting")
for i in range(0, ITERATIONS):
    if (i % 100 == 0):
        print("TEST     : Iteration " + str(i))
    ph = random.choice(list(m.pop.get_current_generation()))
    if random.random() < get_desirability(ph):
        ph.yes += 1
    else:
        ph.no += 1

    new_generation = m.step()
    if new_generation is not None:
        gen_desirabilities.append(get_generation_desirability(new_generation))
        gen_avg_desirabilities.append(get_generation_average_desirability(new_generation))
        best_desirabilities.append(get_best_desirability(m.pop))

print("TEST     : Voting finished")
print("RESULT   : Desirability score of all time best: " +
        str(get_best_desirability(m.pop)))
for ph in m.pop.get_current_generation():
    print("Phenotype " + ph.get_binary_string() + " has desirability " +
            str(get_desirability(ph)))

print("RESULT   : development of generation desirabilities")
for i in range(len(gen_desirabilities)):
    print(str(i) + "\t" + str(gen_desirabilities[i]) + "\t" +
            str(gen_avg_desirabilities[i]) + "\t" +
            str(best_desirabilities[i]))

print("RESULT   : the best voted phenotypes")
for ph in m.pop.get_best(10, randomness=0):
    print(str(ph) + "\t" +
            str(ph.yes) + "/" + str(ph.no) + "\t" + str(get_desirability(ph)))

print("RESULT   : strand winners")
for ph in m.pop.winners:
    print(str(ph) + "\t" +
            str(ph.yes) + "/" + str(ph.no) + "\t" + str(get_desirability(ph)))

# print("TRY      : neural network")
# gene_count = len(Phenotype(-1).all_genes)
# neural_network = NN(gene_count, 3, 1)
# neural_network.train(nn_train_set)
# neural_network.test(nn_train_set)
