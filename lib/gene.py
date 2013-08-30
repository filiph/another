import array
import random

class Gene:
    """A single gene"""
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.bits = array.array('B')  # array of bytes

    @property
    def as_string(self):
        self.check_initialized()
        str_list = []
        for b in self.bits:
            str_list.append(str(b))
        return ''.join(str_list)

    @as_string.setter
    def as_string(self, string):
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
        self.as_int = 0  # delete and initialize bits
        for i in range(0, len(self.bits)):
            self.bits[i] = a_gene.bits[i] if random.random() < relative_strength else b_gene.bits[i]

    @property
    def as_bool(self):
        self.check_initialized()
        assert(self.size == 1)
        return self.bits[0] == 1

    @as_bool.setter
    def as_bool(self, value):
        assert(self.size == 1)
        if len(self.bits) is 0:
            # not initialized
            self.bits.append(0)
        assert(len(self.bits) == 1)
        self.bits[0] = 1 if value is True else 0

    @property
    def as_int(self):
        self.check_initialized()
        return int(self.as_string, 2)

    @as_int.setter
    def as_int(self, value):
        assert(2 ** self.size > value)
        string = bin(value)[2:].zfill(self.size)
        self.as_string = string

    @property
    def max_int(self):
        self.check_initialized()
        return 2 ** self.size - 1

    def check_initialized(self):
        assert(len(self.bits) == self.size)

    @property
    def as_relative_value(self):
        return self.as_int / float(self.max_int)

    def __str__(self):
        return str(self.bits)

    def randomize(self):
        self.as_int = 0  # zero-out
        for i in range(0, self.size):
            self.bits[i] = random.choice([0, 1])
