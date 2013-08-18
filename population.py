import random

from phenotype import Phenotype

class Population:
    def __init__(self):
        self.phenotypes = []
        self.winners = []
        self.current = None
        self.current_generation = -1
        self.latest_idn = 0

    GENERATION_SIZE = 20  # Should be even.
    FIRST_GENERATION_SIZE = GENERATION_SIZE * 1
    CROSSOVER_PROBABILITY = 0.7
    SHARED_FITNESS_SIGMA = 0.05
    SHARED_FITNESS_ALPHA = 1
    MUTATION_RATE = 0.05
    MIN_VOTES = 10  # Minimum number of yes/no votes to calculate fitness

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
            if self.phenotype_in_one_of_strands(candidate):
                continue  # Already taken care of.
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

    def hamming_distance(ph1, ph2):
        s1 = ph1.get_binary_string()
        s2 = ph2.get_binary_string()
        assert len(s1) == len(s2)
        return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))


    # from http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.33.8352&rep=rep1&type=pdf, p20-21
    def get_shared_fitness(self, ph, pool):
        print("Calculating shared fitness for {0}".format(ph))
        str_len = len(ph.get_binary_string())
        niche_count = 0
        for candidate in pool:
            dist = Population.hamming_distance(candidate, ph) / float(str_len)
            if dist < Population.SHARED_FITNESS_SIGMA:
                niche_count += 1 - (dist / Population.SHARED_FITNESS_SIGMA) ** Population.SHARED_FITNESS_ALPHA
                print("- found a phenotype in radius (dist={0}) - {1}".format(dist, candidate))
        shared_fitness = ph.get_fitness_from_votes() / niche_count
        print("- final fitness = {0}".format(shared_fitness))
        return shared_fitness

    def get_random_tournament_winner(self, pool):
        contestant1 = random.choice(pool)
        contestant2 = None
        while True:
            contestant2 = random.choice(pool)
            if contestant2 != contestant1:
                break
        if self.get_shared_fitness(contestant1, pool) > self.get_shared_fitness(contestant2, pool):
            return contestant1
        else:
            return contestant2

    def create_from_crossover_genes(self, ph1, ph2):
        assert(len(ph1.all_genes) == len(ph2.all_genes))
        a = random.randint(0, len(ph1.all_genes) - 1)
        b = random.randint(0, len(ph1.all_genes) - 1)
        self.latest_idn += 1
        child1 = Phenotype(self.latest_idn)
        self.latest_idn += 1
        child2 = Phenotype(self.latest_idn)
        parents = [ph1, ph2]
        for i in range(len(child1.all_genes)):
            child1.all_genes[i] = parents[0].all_genes[i]
            child2.all_genes[i] = parents[1].all_genes[i]
            if i == a or i == b:
                parents[0], parents[1] = parents[1], parents[0]
        return child1, child2

    def create_from_crossover_bits(self, ph1, ph2):
        ph1dna = ph1.get_binary_string()
        ph2dna = ph2.get_binary_string()
        assert(len(ph1dna) == len(ph2dna))
        a = random.randint(0, len(ph1dna) - 1)
        b = random.randint(0, len(ph2dna) - 1)
        self.latest_idn += 1
        child1 = Phenotype(self.latest_idn)
        child1dna = []
        self.latest_idn += 1
        child2 = Phenotype(self.latest_idn)
        child2dna = []
        parents_dna = [ph1dna, ph2dna]
        for i in range(len(ph1dna)):
            child1dna.append(parents_dna[0][i])
            child2dna.append(parents_dna[1][i])
            if i == a or i == b:
                parents_dna[0], parents_dna[1] = parents_dna[1], parents_dna[0]
        child1.set_from_dna("".join(child1dna))
        child2.set_from_dna("".join(child2dna))
        return child1, child2



    def create_new_generation(self):
        print("Creating a new generation number " + str(self.current_generation + 1))
        old_generation = list(self.get_current_generation())
        print("  - old generation")
        for member in old_generation:
            print("    - {0} ({1}/{2})".format(member, member.yes, member.no))
        print("Mating...")
        self.current_generation += 1
        children = []
        for i in range(int(Population.GENERATION_SIZE / 2)):
            winner1 = self.get_random_tournament_winner(old_generation)
            winner2 = self.get_random_tournament_winner(old_generation)
            if random.random() < Population.CROSSOVER_PROBABILITY:
                child1, child2 = self.create_from_crossover_bits(winner1, winner2)
            else:
                self.latest_idn += 1
                child1 = Phenotype(self.latest_idn)
                child1.set_from_dna(winner1.get_binary_string())
                self.latest_idn += 1
                child2 = Phenotype(self.latest_idn)
                child2.set_from_dna(winner2.get_binary_string())
            if Population.MUTATION_RATE > 0:
                child1.mutate(Population.MUTATION_RATE)
                child2.mutate(Population.MUTATION_RATE)
            child1.generation = self.current_generation
            child2.generation = self.current_generation
            children.append(child1)
            children.append(child2)
            print("Parents and children:")
            print(" - " + str(winner1))
            print(" - " + str(winner2))
            print(" - " + str(child1))
            print(" - " + str(child2))
        self.phenotypes.extend(children)
        return children


# pop = Population()
# pop.create_first_generation(5)
# print(pop.phenotypes)
