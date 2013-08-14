# Used to find the best evolution strategy.

import os
import sys
import random
import pickle

from population import *

DESIRABLEOUTCOMES = [
        "11111111",
        "00000000",
        "10101010",
        "01010101"]

ITERATIONS = 5000
SUCCESS_THRESHOLD = 3.0  # 1.0 is a 100% match for each desirable
                         # outcome.


def get_match(dna1, dna2):
    assert(len(dna1) == len(dna2))
    matched = 0
    for i in range(0, len(dna1)):
        if dna1[i] == dna2[i]:
            matched += 1
    return matched / float(len(dna1))

last_few_phenotypes = []
MAX_LAST_FEW_PHENOTYPES = 5

def get_desirability(ph, sameness_penalty=False):
    bestresult = 0
    for outcome in DESIRABLEOUTCOMES:
        result = get_match(ph.get_binary_string(), outcome)
        if sameness_penalty:
            samepenalty = 0
            for recent_ph in last_few_phenotypes:
                p = get_match(ph.get_binary_string(),
                        recent_ph.get_binary_string())
                p = p / 2.0  # dampen the 'sameness' penalty
                if p > samepenalty:
                    samepenalty = p
            result -= samepenalty
        if result > bestresult:
            bestresult = result
    if len(last_few_phenotypes) > MAX_LAST_FEW_PHENOTYPES:
        last_few_phenotypes.pop(0)
    last_few_phenotypes.append(ph)
    return bestresult

def get_current_generation_desirability(pop):
    score = 0
    for outcome in DESIRABLEOUTCOMES:
        bestresult = 0
        for ph in pop.get_current_generation():
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
pop = Population()
pop.create_first_generation()

gen_desirabilities = []
best_desirabilities = []

print("TEST     : Starting voting")
for i in range(0, ITERATIONS):
    if (i % 100 == 0):
        print("TEST     : Iteration " + str(i))
    ph = pop.get_next()
    if random.random() < get_desirability(ph, sameness_penalty=True):
        ph.yes += 1
    else:
        ph.no += 1

    if pop.is_ready_for_next_generation():
        gen_desirabilities.append(get_current_generation_desirability(pop))
        best_desirabilities.append(get_best_desirability(pop))
        print("TEST     : Creating new generation (" +
                str(pop.current_generation + 1) + ")")
        children = pop.create_new_generation()

print("TEST     : Voting finished")
print("RESULT   : Desirability score of all time best: " +
        str(get_best_desirability(pop)))
for ph in pop.get_current_generation():
    print("Phenotype " + ph.get_binary_string() + " has desirability " +
            str(get_desirability(ph)))

print("RESULT   : development of generation desirabilities")
for i in range(len(gen_desirabilities)):
    print(str(i) + "\t" + str(gen_desirabilities[i]) + "\t" +
            str(best_desirabilities[i]))
