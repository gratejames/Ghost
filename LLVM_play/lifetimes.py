import nodes


class life:
    starts = []
    uses = []
    terms = []
    dead = True
    startforced = None
    endforced = None

    def __init__(self, start):
        self.starts = [start]
        self.uses = []
        self.terms = []

    def __repr__(self):
        sf = " sf" + self.startforced if self.startforced is not None else ""
        ef = " ef" + self.endforced if self.endforced is not None else ""
        return f"({self.starts})-({self.uses})({self.terms})" + sf + ef


class lifetimes:
    def getname(self, name, function=None):
        if function is None:
            function = self.function
        if isinstance(function, nodes.Function):
            function = function.name
        return function + name

    def use(self, item, force=None):
        if isinstance(item, nodes.RegisterReference):
            l = self.lifes[self.getname(item.name)]
            l.uses.append(self.i)
            # if force is not None:
            #     l.endforced = force

    def create(self, name, force=None):
        l = life(self.i)
        self.lifes[self.getname(name)] = l
        # if force is not None:
        #     l.startforced = force

    def force(self, name, regname, end=False):
        if end:
            self.lifes[self.getname(name)].endforced = regname
        else:
            self.lifes[self.getname(name)].startforced = regname

    def __init__(self, arr):
        self.arr = arr  # Original array of nodes
        self.lifes = {}  # lifes[registername] = class life
        self.function = None
        for self.i, node in enumerate(self.arr):
            match node:
                case nodes.Function():
                    self.function = node
                    for old_life in self.lifes.values():
                        old_life.terms.append(self.i)
                    for i, a in enumerate(node.arguments):
                        self.create(a.register)
                        self.force(a.register, f"R{i}")

                case nodes.FunctionDefArgument():
                    self.lifes[self.getname(node.register)].uses.append(self.i)
                case nodes.Load():
                    self.create(node.result)
                case nodes.BiOp():
                    self.use(node.op1, "R0")
                    self.use(node.op2)
                    self.create(node.result, "R0")
                case nodes.Call():
                    for i, a in enumerate(node.callargs):
                        self.use(a, f"R{i}")
                    self.create(node.result)
                case nodes.Store():
                    self.use(node.pre_node)
                case nodes.Ret():
                    self.use(node.pre_node)
                case nodes.Icmp():
                    self.use(node.op1)
                    self.use(node.op2)
                    self.create(node.result, "JR")
                case nodes.BranchCond():
                    self.use(node.cmp)
                case nodes.lateAlloc():
                    pass
                case nodes.Label():
                    pass
                case nodes.Branch():
                    pass
                case _:
                    print("Unknown register lifetime effects from", node)
                    exit()

    def process(self):
        for l in self.lifes.values():
            l.terms = [max(l.uses)]

    def textout(self):
        ret_lifes = []
        names = []
        for i, line in enumerate(self.arr):
            textline = ""
            for name, life in self.lifes.items():
                if i in life.starts:
                    if i in life.terms:
                        textline += "/" + name
                    else:
                        names.append(name)
                        textline += name + " "
                    life.dead = False
                elif life.dead:
                    textline += " " * (len(name) + 1)
                elif i in life.uses and i in life.terms:
                    textline += "/" + " " * len(name)
                    life.dead = True
                elif i in life.uses:
                    textline += "<" + " " * len(name)
                elif i in life.terms:
                    textline += "X" + " " * len(name)
                    life.dead = True
                else:
                    textline += "|" + " " * len(name)
            ret_lifes.append(textline)
        for life in self.lifes.values():
            life.dead = True
        return ret_lifes
        # return ["Woah"] * len(self.arr)

    #

    def overlap(self, a, b):
        assert len(a.starts) == len(a.terms)
        assert len(b.starts) == len(b.terms)
        a_ranges = []
        b_ranges = []
        for i in range(len(a.starts)):
            a_ranges.append((a.starts[i], a.terms[i]))
        for i in range(len(b.starts)):
            b_ranges.append((b.starts[i], b.terms[i]))
        for a_start, a_end in a_ranges:
            for b_start, b_end in b_ranges:
                if a_start < b_start and b_start < a_end:
                    return True
                if a_start < b_end and b_end < a_end:
                    return True

        # print(a_ranges, b_ranges)
        return False

    def combine(self, a, b):
        if not self.overlap(a, b):
            a.starts += b.starts
            a.uses += b.uses
            a.terms += b.terms
            a.forced = None
            return True
        else:
            return False

    hardwareRegisters = ["R0", "R1", "R2", "R3", "JR", "AR"]
    GPRs = ["R1", "R2", "R3"]

    def updateName(self, life, oldname, newname):
        # print(life, self.lifes.get(oldname, None), self.lifes.get(newname, None))
        del self.lifes[oldname]
        if newname in self.lifes:
            c_success = self.combine(self.lifes[newname], life)
            if not c_success:
                self.lifes[oldname] = life
            else:
                self.translations[oldname] = newname
            return c_success
        else:
            self.lifes[newname] = life
            self.translations[oldname] = newname
            return True
        # print(life, self.lifes.get(oldname, None), self.lifes.get(newname, None))

    def resolve(self):
        self.translations = {}
        # print(self.lifes)
        for r in self.hardwareRegisters:
            if r not in self.lifes.keys():
                l = life(0)
                l.starts = []
                self.lifes[r] = l

        Free = ["R1", "R2", "R3"]
        # Apply forcing
        for name, lifetime in list(self.lifes.items()):
            sf = lifetime.startforced
            ef = lifetime.endforced
            if sf is not None or ef is not None:
                if (sf is not None and ef is not None) and sf != ef:
                    print("Start force and end force are not equal!")
                    print(lifetime)
                    exit()
                f = sf if ef is None else ef
                if not self.updateName(lifetime, name, f):
                    # Overlap!
                    print(lifetime, "and", self.lifes[f], "overlap!")
                    # exit()

        for i, line in enumerate(self.arr):
            for name, lifetime in list(self.lifes.items()):
                if i in lifetime.terms:
                    if name in self.GPRs:
                        Free.append(name)
            for name, lifetime in list(self.lifes.items()):
                if i in lifetime.starts:
                    if name not in self.hardwareRegisters:  # Needs register
                        if len(Free) > 0:
                            Free.sort()
                            r = Free.pop(0)
                            self.updateName(lifetime, name, r)
                        else:
                            print(
                                "No free registers to allocate!! Spilling not supported yet"
                            )
                            exit()
