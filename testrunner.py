# Used to find the best evolution strategy.

import os
import sys
import random
import pickle

from population import *

DESIRABLEOUTCOMES = [
        "11111111",
        #"00000000",
        #"10101010",
        "01010101"]

ITERATIONS = 10000
SUCCESS_THRESHOLD = 3.0  # 1.0 is a 100% match for each desirable
                         # outcome.

MUTATION_RATE = 0.1

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
    return result

def get_current_generation_desirability(pop):
    score = 0
    for outcome in DESIRABLEOUTCOMES:
        bestresult = 0
        for ph in pop.get_current_generation():
            result = get_match(ph.get_binary_string(), outcome)
            if result > bestresult:
                bestresult = result
        score += bestresult
    return result


print("TEST     : Creating random sample")
pop = Population()
pop.create_first_generation()

print("TEST     : Starting voting")
for i in range(0, ITERATIONS):
    #print("TEST     : Iteration " + str(i))
    ph = pop.get_next()
    if random.random() < get_desirability(ph):
        ph.yes += 1
    else:
        ph.no += 1

    if pop.is_ready_for_next_generation():
        print("TEST     : Creating new generation (" +
                str(pop.current_generation) + ")")
        children = pop.create_new_generation()
        for child in children:  # TODO: move this into create_new_generation
            child.mutate(MUTATION_RATE)

print("TEST     : Voting finished")
print("RESULT   : Desirability score of generation: " +
        str(get_current_generation_desirability(pop)))
for ph in pop.get_current_generation():
    print("Phenotype " + ph.get_binary_string() + " has desirability " +
            str(get_desirability(ph)))

