# Used to find the best evolution strategy.

import os
import sys
import random
import pickle

from population import *

DESIRABLEOUTCOMES = [
        "1111111111111111",
        "0000000000000000",
        "1010101010101010",
        "0101010101010101"]

ITERATIONS = 50000


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

def get_current_generation_average_desirability(pop):
    score = 0
    for ph in pop.get_current_generation():
        score += get_desirability(ph)
    return score / float(Population.GENERATION_SIZE)

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
gen_avg_desirabilities = []
best_desirabilities = []

print("TEST     : Starting voting")
for i in range(0, ITERATIONS):
    if (i % 100 == 0):
        print("TEST     : Iteration " + str(i))
    #ph = pop.get_next()
    ph = random.choice(list(pop.get_current_generation()))
    if random.random() < get_desirability(ph):
        ph.yes += 1
    else:
        ph.no += 1

    if pop.is_ready_for_next_generation():
        gen_desirabilities.append(get_current_generation_desirability(pop))
        gen_avg_desirabilities.append(get_current_generation_average_desirability(pop))
        best_desirabilities.append(get_best_desirability(pop))
        # print("TEST     : Identifying strand winners")
        # pop.identify_winners()
        print("TEST     : Creating new generation (" +
                str(pop.current_generation + 1) + ")")
        children = pop.create_new_generation()
        # gen = pop.current_generation
        # children = pop.create_first_generation()
        # for child in children:
        #     child.generation = gen + 1
        # pop.current_generation = gen + 1


print("TEST     : Voting finished")
print("RESULT   : Desirability score of all time best: " +
        str(get_best_desirability(pop)))
for ph in pop.get_current_generation():
    print("Phenotype " + ph.get_binary_string() + " has desirability " +
            str(get_desirability(ph)))

print("RESULT   : development of generation desirabilities")
for i in range(len(gen_desirabilities)):
    print(str(i) + "\t" + str(gen_desirabilities[i]) + "\t" +
            str(gen_avg_desirabilities[i]) + "\t" +
            str(best_desirabilities[i]))

print("RESULT   : the best voted phenotypes")
for ph in pop.get_best(10, randomness=0):
    print(str(ph) + "\t" +
            str(ph.yes) + "/" + str(ph.no) + "\t" + str(get_desirability(ph)))

print("RESULT   : strand winners")
for ph in pop.winners:
    print(str(ph) + "\t" +
            str(ph.yes) + "/" + str(ph.no) + "\t" + str(get_desirability(ph)))
