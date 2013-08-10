from gene import *

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
        self.trees_seed = Gene(2, 4)

        self.set_all_genes()

    def __str__(self):
        str_list = ["Phenotype ", str(self.idn), ": "]
        for gene in self.all_genes:
            str_list.append(gene.get_binary_string())
        return ''.join(str_list)

    def set_all_genes(self):
        self.all_genes = []
        for attr, value in vars(self).items():
            if isinstance(value, Gene):
                self.all_genes.append(value)

    def get_binary_string(self):
        str_list = []
        for gene in sorted(self.all_genes, key = lambda gene: gene.pos):
            str_list.append(gene.get_binary_string())
        return "".join(str_list)

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

        for attr, gene in vars(self).items():
            if isinstance(gene, Gene):
                assert(hasattr(parent_a, attr))
                assert(hasattr(parent_b, attr))
                gene.set_from_mating(getattr(parent_a, attr), getattr(parent_b, attr), relative_strength)

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
