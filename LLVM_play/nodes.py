class Function:
    def __init__(self):
        self.name = ""
        self.attrs = []
        self.lines = []
        self.arguments = []
        self.number = ""
        self.ret_type = ""

    def __repr__(self):
        return f"{self.name}: ({' '.join([a.register for a in self.arguments])})"

    def dump(self):
        print(
            f"#{self.number} {self.ret_type} {self.name}({', '.join(str(x) for x in self.arguments)})",
            "{",
        )
        for l in self.lines:
            print("\t", l)
        print("}")


class Label:
    name: str

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.name}:"


class Node:
    pre_node: "Node"
    label: Label | None = None
    ty = ""
    visited = False
    indent = 0
    effect_order = 0

    def __repr__(self):
        return f"errnode {self.ty} from <{self.pre_node}>"


class Block:
    final: Node | None

    def __init__(self, label, preds=[]):
        self.label = label
        self.registers = {}
        self.memoryeffects = {}
        self.sideeffects = []
        self.preds = preds
        self.type = "branch"
        self.final = None
        self.referenced = False
        self.sequence = []

    def __repr__(self):
        return f"block <{self.label.name} preds {len(self.preds)} final {self.final}>"


class FunctionDef(Node):
    ret: Node
    blocks: list[Block]


class FunctionDefArgument(Node):
    def __init__(self, ty, register):
        self.ty = ty
        self.register = register

    def __repr__(self):
        return f"arg {self.ty} {self.register}"


class RegisterReference(Node):
    name: str

    def __repr__(self):
        # return f"reg_ref {self.ty} {self.name} from <{self.pre_node}>"
        return f"reg_ref {self.name}"


class GlobalReference(Node):
    name: str

    def __repr__(self):
        # return f"reg_ref {self.ty} {self.name} from <{self.pre_node}>"
        return f"global_ref {self.name}"


class Pointer(Node):
    def __init__(self, ty, address):
        self.ty = ty
        self.address = address

    def __repr__(self):
        return f"ptr <{self.address}>"


class StackVar(Node):
    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return f"Stackvar <{self.address}>"


# class MemoryNode(Node):
#     pointer: Node


class lateAlloc(Node):
    def __init__(self, idx, register):
        self.idx = idx
        self.register = register

    def __repr__(self):
        return f"Alloc {self.idx} (Oldname: {self.register})"


class Store(Node):
    pointer: Node

    def __repr__(self):
        return f"store val <{self.pre_node}>"


class Branch(Node):
    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return f"Jump to <{self.label}>"


class BranchCond(Node):
    def __init__(self, cmp, label_true, label_false):
        self.cmp = cmp
        self.label_true = label_true
        self.label_false = label_false

    def __repr__(self):
        return f"BranchC {self.cmp}: <{self.label_true}> <{self.label_false}>"


class Ret(Node):
    def __init__(self, ty, pre_node):
        self.ty = ty
        self.pre_node = pre_node

    def __repr__(self):
        return f"ret from <{self.pre_node}>"


class UnresolvedString(Node):
    value: str

    def __repr__(self):
        return f"UNRESOLVED {self.ty} v:{self.value}"


class Constant(Node):
    value: str

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"const {self.ty} v:{self.value}"


# class ASM(Node):
#     def __init__(self, contents):
#         self.contents = contents


class Void(Node):
    pass


class Operator(Node):
    result: RegisterReference


class Alloca(Operator):
    def __init__(self, ty, align):
        self.ty = ty
        self.align = align

    def __repr__(self):
        return f"alloca {self.ty}"


class Call(Operator):
    def __init__(self, ty, name, callargs):
        self.ty = ty
        self.name = name
        self.callargs = callargs

    def __repr__(self):
        return f"Call {self.ty} {self.name}({', '.join(str(x) for x in self.callargs)})"


class Load(Operator):
    pointer: Node
    align: int

    def __repr__(self):
        return f"load from ({self.pointer})"


class BiOp(Operator):
    def __init__(self, op, op1, op2):
        self.op = op
        self.op1 = op1
        self.op2 = op2

    def __repr__(self):
        return f"{self.op} <{self.op1}> and <{self.op2}>"


class Icmp(Operator):
    type = "i1"

    def __init__(self, op, op1, op2):
        self.op = op
        self.op1 = op1
        self.op2 = op2

    def __repr__(self):
        return f"Compare {self.op}: <{self.op1}> <{self.op2}>"


class GetElementPtr(Operator):
    idxs = []

    def __init__(self, idxs):
        self.idxs = idxs


class ZeroExtend(Operator):
    pass
    # New type is .ty
    # Old type is .pre_node.ty, probably
    # def __init__(self):
