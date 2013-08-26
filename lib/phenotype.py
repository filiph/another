from lib.gene import *

class Phenotype:
    INITIAL_HITPOINTS = 10

    def __init__(self, idn):
        self.idn = idn
        self.generation = -1

        self.yes = 0
        self.no = 0
        self.meh = 0

        self.hp = Phenotype.INITIAL_HITPOINTS

        self.show_trees = Gene(0, 1)
        self.sun_position = Gene(1, 3)  # 8 different positions (2**3)
        self.trees_seed = Gene(2, 2)
        self.arbitrary_a = Gene(3, 2)
        self.arbitrary_b = Gene(4, 2)
        self.arbitrary_c = Gene(5, 2)
        self.arbitrary_d = Gene(6, 2)
        self.arbitrary_e = Gene(7, 2)

        self.set_all_genes()

    def __str__(self):
        str_list = ["Phenotype ", str(self.idn), ": "]
        for gene in self.all_genes:
            str_list.append(gene.get_binary_string())
        str_list.append(" (f={0})".format(self.get_fitness_from_votes()))
        return ''.join(str_list)

    def set_all_genes(self):
        self.all_genes = []
        for attr, value in vars(self).items():
            if isinstance(value, Gene):
                self.all_genes.append(value)

    def get_fitness_from_votes(self):
        if self.yes + self.no == 0:
            return 0
        return (1 + (self.yes - self.no) / float(self.yes + self.no)) / float(2)

    def get_binary_string(self):
        str_list = []
        for gene in sorted(self.all_genes, key = lambda gene: gene.pos):
            str_list.append(gene.get_binary_string())
        return "".join(str_list)

    # TODO: make this based on genes, or use Gray for num attributes
    def get_similarity(self, other):
        dna1 = self.get_binary_string()
        dna2 = other.get_binary_string()
        l = len(dna1)
        assert(l, len(dna2))
        matched = 0
        for i in range(0, l):
            if dna1[i] == dna2[i]:
                matched += 1
        return matched / float(len(dna1)) 

    def randomize(self):
        for gene in self.all_genes:
            gene.randomize()

    def set_from_dna(self, dna):
        pos = 0
        for gene in sorted(self.all_genes, key = lambda gene: gene.pos):
            gene.set_from_string(dna[pos:pos + gene.size])
            pos += gene.size

    def set_from_mating(self, parent_a, parent_b, relative_strength):
        self.parent_idns = (parent_a.idn, parent_b.idn)
        if hasattr(parent_a, "generation"):
            self.generation = parent_a.generation + 1
        else:
            self.generation = 0

        if hasattr(parent_b, "generation"):
            if parent_b.generation >= self.generation:
                self.generation = parent_b.generation + 1
        # TODO ^^^ there might be a bug here since generation doesn't go up

        for attr, gene in vars(self).items():
            if isinstance(gene, Gene):
                assert(hasattr(parent_a, attr))
                assert(hasattr(parent_b, attr))
                gene.set_from_mating(getattr(parent_a, attr), getattr(parent_b, attr), relative_strength)

    def mutate(self, rate):
        for gene in self.all_genes:
            # TODO: flip via crossover or according to gene borders
            for i in range(0, len(gene.bits)):
                if random.random() < rate:
                    # flip bit
                    gene.bits[i] = 1 if gene.bits[i] == 0 else 0


# ph_a = Phenotype(0)
# ph_a.randomize()
# print(ph_a)
# ph_b = Phenotype(1)
# ph_b.randomize()
# print(ph_b)
# ph_c = Phenotype(2)
# ph_c.set_from_mating(ph_a, ph_b, 0.5)
# print(ph_c)

# 
# g = Gene(0, 2)
# g.randomize()
# print(g)
# print(g.get_max_int())
# print(g.get_relative_value())
