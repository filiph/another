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

ITERATIONS = 10000


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




m = Manager(size=10)
m.start()
runner = Runner(m, objective_function=get_desirability)

runner.run(2000)

print("Runner completed with end result: {0:.0f} improvement".format(runner.improvement * 100))

