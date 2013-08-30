import array
import random

class Gene:
    """A single gene"""
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.bits = array.array('B')

    def set_from_string(self, string):
        assert(len(string) == self.size)
        del self.bits[:]
        i = 0
        for ch in string:
            if ch == '1':
                self.bits.append(1)
            elif ch == '0':
                self.bits.append(0)
            else:
                raise Exception(string, "Initialization string can only have zeroes or ones.")
            i += 1

    def set_from_mating(self, a_gene, b_gene, relative_strength):
        assert(isinstance(a_gene, Gene))
        assert(isinstance(b_gene, Gene))
        self.set_from_int(0)  # delete and initialize bits
        for i in range(0, len(self.bits)):
            self.bits[i] = a_gene.bits[i] if random.random() < relative_strength else b_gene.bits[i]

    def set_from_int(self, value):
        assert(2 ** self.size > value)
        str = bin(value)[2:].zfill(self.size)
        self.set_from_string(str)

    def get_bool(self):
        self.check_initialized()
        assert(self.size == 1)
        return self.bits[0] == 1

    def get_int(self):
        self.check_initialized()
        return int(self.get_binary_string(), 2)

    def get_max_int(self):
        self.check_initialized()
        return 2 ** self.size - 1

    def get_binary_string(self):
        self.check_initialized()
        str_list = []
        for b in self.bits:
            str_list.append(str(b))
        return ''.join(str_list)

    def check_initialized(self):
        assert(len(self.bits) == self.size)

    def get_relative_value(self):
        return self.get_int() / float(self.get_max_int())

    def __str__(self):
        return str(self.bits)

    def randomize(self):
        self.set_from_int(0)  # zero-out
        for i in range(0, self.size):
            self.bits[i] = random.choice([0, 1])

# g = Gene(0, 7)
# print(g.size)
# g.set_from_string("1001")
# print(g)
# g.randomize()
# print(g)
# g.set_from_int(15)
# print(g)
# print(g.get_int())
