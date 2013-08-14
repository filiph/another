import random

from phenotype import Phenotype

class Population:
    def __init__(self):
        self.phenotypes = []
        self.current = None
        self.current_generation = -1
        self.latest_idn = 0

    GENERATION_SIZE = 4
    FIRST_GENERATION_SIZE = GENERATION_SIZE * 5
    MUTATION_RATE = 0.2
    MIN_VOTES = 3  # Minimum number of yes/no votes to calculate fitness

    def create_first_generation(self):
        for i in range(0, Population.FIRST_GENERATION_SIZE):
            ph = Phenotype(i)
            ph.generation = 0
            ph.randomize()
            self.phenotypes.append(ph)
            self.latest_idn = i
        self.current_generation = 0
        self.current = self.phenotypes[0]

    def get_next(self, check_callback=None):
        """ Returns the next phenotype to be shown. """
        assert(len(self.phenotypes) > 0)
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

    BEST_PICK_RANDOMNESS_FACTOR = 2.0

    def get_best(self, num):
        def get_score(ph):
            # can get old ones without any yes/no histroy
            if ph.yes + ph.no == 0: return 0.0
            return (ph.yes - ph.no) / float(ph.yes + ph.no) + \
                    (random.random() - 0.5) * Population.BEST_PICK_RANDOMNESS_FACTOR
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

    def calculate_fitness(ph):
        assert(ph.yes + ph.no > 0)
        return (ph.yes - ph.no) / float(ph.yes + ph.no)

    def create_new_generation(self):
        print("Creating a new generation number " + str(self.current_generation + 1))
        parents = list(self.get_current_generation())
        parents = parents[:int(Population.GENERATION_SIZE / 2)]
        parents.extend(self.get_best(int(Population.GENERATION_SIZE / 2)))
        parents.sort(key = Population.calculate_fitness)
        # Create a pool of candidates. The more successful get more slots
        candidates = []
        for i in range(0, len(parents)):
            slots_taken = i  # simple function - more fitness => more slots
            for j in range(0, slots_taken):
                candidates.append(parents[i])
            print("Phenotype " + parents[i].get_binary_string() + " gets " + str(slots_taken) + " slots in the pool")
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
            self.latest_idn += 1
            child = Phenotype(self.latest_idn)
            child.set_from_mating(parent_a, parent_b, 0.5)
            child.generation = self.current_generation
            child.mutate(Population.MUTATION_RATE)
            self.phenotypes.append(child)
            children.append(child)
            count += 1
            print("- newborn phenotype: " + child.get_binary_string())
        return children


# pop = Population()
# pop.create_first_generation(5)
# print(pop.phenotypes)
