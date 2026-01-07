class Instruction:
    pass


class LDA(Instruction):
    def __init__(self, register, pointer):
        self.register = register
        self.pointer = pointer

    def __repr__(self):
        return f"LDA {self.register} ${self.pointer}"


class LDV(Instruction):
    def __init__(self, register, value):
        self.register = register
        self.value = value

    def __repr__(self):
        return f"LDV {self.register} {self.value}"


class Compare(Instruction):
    def __init__(self, op, op1, op2):
        self.op = op
        self.op1 = op1
        self.op2 = op2

    def __repr__(self):
        return f"psuedo Compare <{self.op1} {self.op} {self.op2}>"


class CALL(Instruction):
    def __init__(self, label, args):
        self.args = args
        self.label = label

    def __repr__(self):
        return f"CALL {self.label} ({', '.join(str(x) for x in self.args)})"


class RET(Instruction):
    def __init__(self, retval):
        self.retval = retval

    def __repr__(self):
        return f"RET <{self.retval}>"
