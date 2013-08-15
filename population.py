import random

from phenotype import Phenotype

class Population:
    def __init__(self):
        self.phenotypes = []
        self.winners = []
        self.current = None
        self.current_generation = -1
        self.latest_idn = 0

    GENERATION_SIZE = 5
    FIRST_GENERATION_SIZE = GENERATION_SIZE * 1
    MUTATION_RATE = 0.1
    MIN_VOTES = 20  # Minimum number of yes/no votes to calculate fitness

    # TODO: make these dynamic - the more winners we have, the narrower their strands are?
    MUTATION_THRESHOLD = 0.7  # after certain success rate, only mutate without mating
    STRAND_COMPLETE_THRESHOLD = 0.9  #  after certain success rate, this phenotype is marked as complete and similar (as defined by STRAND_RANGE) phenotypes are discouraged/forbidden for mating or being born
    STRAND_RANGE = 0.2  # if a phenotype is (1 - STRAND_RANGE)% similar to a winner phenotype, it is marked as part of its strand

    def create_first_generation(self):
        first_ones = []
        for i in range(0, Population.FIRST_GENERATION_SIZE):
            ph = Phenotype(i)
            ph.generation = 0
            ph.randomize()
            self.phenotypes.append(ph)
            self.latest_idn = i
            first_ones.append(ph)
        self.current_generation = 0
        self.current = self.phenotypes[0]
        return first_ones

    def get_next(self, check_callback=None):
        """ Returns the next phenotype to be shown. """
        assert(len(self.phenotypes) > 0)
        if self.current:
            assert(len(self.phenotypes) > 1)
        candidate = None
        while True:
            candidate = self.get_random()
            if (candidate is not self.current):
                if (check_callback == None):
                    break
                elif check_callback(candidate):
                    break
        self.current = candidate
        return candidate

    def calculate_show_score(self, ph):
        """ Returns int which represents the chance with which the given phenotype should be shown. """
        score = 0
        score += ph.generation + 1  # more recent generations are more likely to show
        score *= 2 if (ph.yes + ph.no < Population.MIN_VOTES) else 1  # non-resolved phenotypes are much more likely to show
        # TODO: cache score - it is retrieved twice per phenotype
        return score

    # inspired by http://stackoverflow.com/a/14916069
    def get_random(self):
        score_sum = 0
        for ph in self.phenotypes:
            score_sum += self.calculate_show_score(ph)
        choice = random.randint(0, score_sum - 1)
        pos = 0
        for ph in self.phenotypes:
            pos += self.calculate_show_score(ph)
            if (choice < pos):
                return ph
        assert(False)

    def get_current_generation(self):
        def current(ph): return ph.generation == self.current_generation
        return filter(current, self.phenotypes)

    BEST_PICK_RANDOMNESS_FACTOR = 0.0

    def get_best(self, num, randomness=BEST_PICK_RANDOMNESS_FACTOR):
        def get_score(ph):
            # can get old ones without any yes/no histroy
            if ph.yes + ph.no == 0: return 0.0
            return (ph.yes - ph.no) / float(ph.yes + ph.no) + \
                    (random.random() - 0.5) * randomness
        return sorted(self.phenotypes, key=get_score, reverse=True)[:num] # TODO: use nlargest

    def is_ready_for_next_generation(self):
        gen = self.get_current_generation()
        if not gen:
            return False
        ready = True
        for ph in gen:
            if ph.yes + ph.no < Population.MIN_VOTES:
                ready = False
                break
        return ready

    # TODO make obsolete by Phenotype.get_fitness_from_votes
    def calculate_fitness(ph):
        assert(ph.yes + ph.no > 0)
        return (ph.yes - ph.no) / float(ph.yes + ph.no)

    def identify_winners(self):
        """ Find if there are any winners and act accordingly. """
        for candidate in self.phenotypes:
            fitness = candidate.get_fitness_from_votes()
            if (fitness > Population.STRAND_COMPLETE_THRESHOLD):
                print("- identified a strand winner: " + str(candidate))
                self.winners.append(candidate)
                # remove all occurrences of strand
                count = len(self.phenotypes)
                self.phenotypes = [ph for ph in self.phenotypes
                        if ph.get_similarity(candidate) < 1 - Population.STRAND_RANGE]
                count -= len(self.phenotypes)
                print("   - deleted " + str(count) + " strand members")
                # TODO: put new randoms in place of the removed from this generation

    def phenotype_in_one_of_strands(self, ph):
        for winner in self.winners:
            if ph.get_similarity(winner) > 1 - Population.STRAND_RANGE:
                return True
        return False

    def create_new_generation(self):
        print("Creating a new generation number " + str(self.current_generation + 1))
        old_generation = list(self.get_current_generation())
        old_generation.sort(key = Population.calculate_fitness)
        print("  - old generation")
        for member in old_generation:
            print("    - {0} ({1}/{2})".format(member, member.yes, member.no))
        parents = old_generation[:int(Population.GENERATION_SIZE / 2)]
        parents.extend(self.get_best(int(Population.GENERATION_SIZE / 2)))
        parents.sort(key = Population.calculate_fitness)
        # Create a pool of candidates. The more successful get more slots
        candidates = []
        for i in range(0, len(parents)):
            slots_taken = i  # simple function - more fitness => more slots
            for j in range(0, slots_taken):
                candidates.append(parents[i])
            print("Phenotype " + str(parents[i]) + " gets " + str(slots_taken) + " slots in the pool")
        # Start mating
        print("Mating...")
        self.current_generation += 1
        count = 0
        children = []
        while count < Population.GENERATION_SIZE:
            parent_a = random.choice(candidates)
            parent_b = random.choice(candidates)
            if parent_a == parent_b:
                continue
            child = Phenotype(self.latest_idn + 1)
            child.set_from_mating(parent_a, parent_b, 0.5)
            child.generation = self.current_generation
            child.mutate(Population.MUTATION_RATE)
            # Don't allow new strand members
            if self.phenotype_in_one_of_strands(child):
                continue
            # Don't allow the same DNA twice
            if any(ph.get_binary_string() == child.get_binary_string() for ph in self.phenotypes):
                continue
            self.phenotypes.append(child)
            children.append(child)
            self.latest_idn += 1
            count += 1
            print("- newborn phenotype: {0} (parents {1})".format(child, child.parent_idns))
        # resolve elites
        for parent in old_generation:
            if parent.get_fitness_from_votes() > Population.MUTATION_THRESHOLD:
                self.latest_idn += 1
                mutant = Phenotype(self.latest_idn)
                mutant.generation = self.current_generation
                mutant.set_from_dna(parent.get_binary_string())
                mutant.mutate(Population.MUTATION_RATE / 2)
                self.phenotypes.append(mutant)
                children.append(mutant)
                print("- new mutant clone: " + str(mutant))
                # self.latest_idn += 1
                # clone = Phenotype(self.latest_idn)
                # clone.generation = self.current_generation
                # clone.set_from_dna(parent.get_binary_string())
                # self.phenotypes.append(clone)
                # children.append(clone)
                parent.generation = self.current_generation # TODO: dehack
                print("- old parent (" + str(parent) + ") kept around")
        return children


# pop = Population()
# pop.create_first_generation(5)
# print(pop.phenotypes)
