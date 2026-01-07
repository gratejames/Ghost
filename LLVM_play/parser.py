import nodes
import parser

# import instructions

# print(data)
# print()


class parser:
    functions = {}
    blocks = []
    cur_func = None

    def __init__(self, filename):
        with open(filename, "r") as f:
            lines = f.read().split("\n")

        class S:
            BODY = 0
            META = 1
            FUNC_O = 2  # Opening
            FUNC = 3

        state = S.BODY

        # Just for type hinting. Will be reset by `; Function Attrs` line
        cur_func = nodes.Function()

        data = {"funcs": [], "globals": {}}

        i = 0
        for line in lines:
            i += 1
            match state:
                case S.BODY:
                    if line.startswith("; ModuleID = "):
                        data["ModuleID"] = line[14:-1]
                        state = S.META
                    elif line.startswith("; Function Attrs: "):
                        cur_func = nodes.Function()
                        cur_func.attrs = line[17:].split(" ")
                        state = S.FUNC_O
                    elif line.startswith("@"):
                        name = line.split(" ")[0]
                        if '"' in line:
                            value = line.split('"')[1]
                        elif "i16" in line:
                            value = int(line.split(" ")[5][:-1])
                        else:
                            assert False, f"Parser can't parse global constant `{line}`"

                        data["globals"][name] = value
                case S.META:
                    if line.strip() == "":
                        state = S.BODY
                        continue
                    k, v = line.split(" = ")
                    if v[0] == '"' and v[-1] == '"':
                        v = v[1:-1]
                    data[k] = v
                case S.FUNC_O:
                    assert line.startswith("define")
                    components = line.split(" ")
                    cur_func.ret_type = components[2]
                    cur_func.number = components[-2][1:]
                    name_and_args = " ".join(components[3:-2])
                    cur_func.name = name_and_args.split("(")[0]
                    arguments = name_and_args.split("(")[1][:-1].split(", ")
                    cur_func.arguments = [
                        nodes.FunctionDefArgument(a.split(" ")[0], a.split(" ")[-1])
                        for a in arguments
                        if a.strip() != ""
                    ]
                    state = S.FUNC
                case S.FUNC:
                    if line.strip() == "}":
                        data["funcs"].append(cur_func)
                        state = S.BODY
                        continue
                    cur_func.lines.append(line.split("!")[0].strip())
                case _:
                    exit(1)

        del cur_func
        self.parsedFuncs = data["funcs"]
        self.globals = data["globals"]

    def stripComments(self, line):
        try:
            return line[: line.index(";")].strip()
        except ValueError:
            return line

    def registers(self):
        return self.blocks[-1].registers

    def memoryeffects(self, neweffects=None):
        if neweffects is not None:
            self.blocks[-1].memoryeffects = neweffects
        return self.blocks[-1].memoryeffects

    def sideeffects(self):
        return self.blocks[-1].sideeffects

    def addMemEffect(self, addr, op):
        if addr in self.memoryeffects():
            self.memoryeffects()[addr].append(op)
        else:
            self.memoryeffects()[addr] = [op]

        # def lower_instruction(self, node: nodes.Node) -> instructions.Instruction:
        #     match node:
        #         case nodes.Load():
        #             ptr = node.pointer
        #             if isinstance(ptr, nodes.Constant):
        #                 instr = instructions.LDV(ptr.ty, ptr.value)
        #             elif isinstance(ptr, nodes.Pointer):
        #                 instr = instructions.LDA(ptr.ty, ptr.address)
        #             else:
        #                 print(f"Failed to lower node {node} to instruction")
        #                 exit()
        #         case nodes.Call():
        #             instr = instructions.CALL(node.name, node.callargs)
        #         # case nodes.Icmp():
        #         #     instr = instructions.Compare(node.op, node.op1, node.op2)
        #         # case nodes.BranchCond():
        #         #     instr = instructions.BranchIf(node.op, node.op1, node.op2)
        #         case nodes.Ret():
        #             instr = instructions.RET(node.pre_node)
        #         case _:
        #             print(f"Failed to lower node `{node}` to instruction")
        #             return node
        #             # exit()
        #     return instr

        # def lowerchain(self, chain):
        #     print(chain)
        #     return chain

        # def lower(self, node: nodes.Node | nodes.Block | nodes.Label) -> nodes.Node:
        #     print("lowering", node, self.cur_func)
        #     match node:
        #         case nodes.Block():
        #             # print("lowering", node)
        #             for pref in node.preds:
        #                 # print(pref)
        #                 pref = self.lower(nodes.Label(pref))
        #             # print("Block final:", node, node.final)
        #             node.final = self.lower(node.final)

        #         case nodes.Label():
        #             for b in self.blocks:
        #                 if b.label.name == node.name:
        #                     b.referenced = True
        #                     return self.lower(b)
        #             print("block of label", node, "not found")
        #             print(self.blocks)
        #             exit()

        #         case nodes.Pointer():
        #             if node.address in self.memoryeffects():
        #                 node.address = self.lowerchain(self.memoryeffects()[node.address])
        #             else:
        #                 node.address = self.lower(node.address)
        #         case nodes.Load():
        #             node.pointer = self.lower(node.pointer)
        #         case nodes.Store():
        #             node.pre_node = self.lower(node.pre_node)
        #         case nodes.BiOp():
        #             node.op1 = self.lower(node.op1)
        #             node.op2 = self.lower(node.op2)
        #         case nodes.RegisterReference():
        #             print(self.blocks)
        #             print(self.cur_func)
        #             print(self.registers())
        #             node = self.lower(self.registers()[node.name])
        #             return node
        #         case nodes.Constant():
        #             pass
        #         case nodes.Icmp():
        #             # return node
        #             pass
        #         case nodes.BranchCond():
        #             node.cmp = self.lower(node.cmp)
        #         case nodes.Branch():
        #             pass
        #         case nodes.Call():
        #             node.callargs = [self.lower(arg) for arg in node.callargs]
        #         case _:
        #             if isinstance(node, nodes.Node):
        #                 try:
        #                     if node.pre_node is not None:
        #                         node.pre_node = self.lower(node.pre_node)
        #                 except AttributeError:
        #                     print("Failed to lower", node)
        #                     exit()
        #             else:
        #                 print("Failed to lower", node)
        #                 # assert node is not None
        #                 exit()
        #     # if isinstance(node, nodes.Node):
        #     #     node = self.lower_instruction(node)
        #     return node

        # def remove_unused_chains(self):
        #     new_memoryeffects = {}
        #     for register, chain in self.memoryeffects().items():
        #         if isinstance(chain[0], nodes.Alloca):
        #             # First, find chains that aren't ever loaded from:
        #             if not any(isinstance(op, nodes.Load) for op in chain):
        #                 # print("Unused chain", register, chain)
        #                 continue
        #         new_memoryeffects[register] = chain
        #     self.memoryeffects(new_memoryeffects)

        # def optimize_constant_chains(self):
        #     new_memoryeffects = {}
        #     for register, chain in self.memoryeffects().items():
        #         if len(chain) == 3:
        #             if (
        #                 isinstance(chain[0], nodes.Alloca)
        #                 and isinstance(chain[1], nodes.Store)
        #                 and isinstance(chain[2], nodes.Load)
        #             ):
        #                 # print("Constant chain", register, chain, type(chain[1].pre_node))
        #                 if isinstance(chain[1].pre_node, nodes.Constant):
        #                     # new_memoryeffects[register] = chain[1].pre_node
        #                     chain[2].pointer = chain[1].pre_node
        #                     continue
        #                 # elif isinstance(chain[1].pre_node, nodes.RegisterReference):
        #                 #     chain[2].pointer = chain[1].pre_node
        #                 #     continue
        #         new_memoryeffects[register] = chain

        #     self.memoryeffects(new_memoryeffects)

        # either ("ty", "val") or ("ty val", None)

    def resolvestring(self, ty, val=None):
        if val is None:
            ty_val = ty.split(" ")
            ty_val = [x for x in ty_val if x != "noundef"]
            if len(ty_val) == 2:
                ty, val = ty_val
            else:
                val = ty_val[-1]
                ty = "Untyped"
        if val[0] == "%":
            rf = nodes.RegisterReference()
            rf.ty = ty
            rf.name = val
            return rf
        elif val[0] == "@":
            gf = nodes.GlobalReference()
            gf.name = val
            return gf
        elif val.isnumeric() or val[0] == "-" and val[1:].isnumeric():
            c = nodes.Constant(int(val))
            c.ty = ty
            return c
        elif val == "void":
            c = nodes.Void()
            return c
        else:
            assert False, f"Unknown string {val}"
            # print("", val)
            # exit(1)

    def parseFunction(self, f):
        # print(f)
        # self.blocks = []
        self.blocks = []
        allocs = {}
        alloc_used = 0
        self.cur_func = f
        self.blocks.append(nodes.Block(nodes.Label(f"{f.name}%entry")))
        for a in f.arguments:
            self.registers()[a.register] = a
            a.visited = True
        for line_number, line in enumerate(f.lines):
            if len(line.strip()) == 0:
                continue
            words = line.split(" ")
            if line[0] == "%" and words[1] == "=":
                op = words[2]
                if op == "alloca":
                    newnode = nodes.Alloca(ty=words[3][:-1], align=words[5])
                    # self.registers()[words[0]] = newnode
                    # self.addMemEffect(words[0], newnode)
                    allocs[words[0]] = alloc_used
                    alloc_used += 1

                elif op in ["add", "sub", "mul", "sdiv", "srem"]:
                    args = " ".join(words[4:]).split(", ")
                    newnode = nodes.BiOp(
                        op=op,
                        op1=self.resolvestring(args[0]),
                        op2=self.resolvestring(args[1]),
                    )
                    self.registers()[words[0]] = newnode

                elif op == "load":
                    newnode = nodes.Load()
                    newnode.ty = words[3]
                    name = words[5][:-1]
                    if name in allocs:
                        pt = nodes.StackVar(allocs[name])
                    else:
                        pt = nodes.Pointer(ty=words[4], address=name)
                    newnode.pointer = pt
                    newnode.align = words[7]
                    self.registers()[words[0]] = newnode
                    self.addMemEffect(newnode.pointer.address, newnode)

                elif op == "icmp":
                    args = " ".join(words[4:]).split(", ")
                    newnode = nodes.Icmp(
                        op=words[3],
                        op1=self.resolvestring(args[0]),
                        op2=self.resolvestring(args[1]),
                    )
                    self.registers()[words[0]] = newnode

                elif op == "call":
                    name = words[4].split("(")[0]
                    args = " ".join(words[4:]).split("(")[1][:-1].split(",")
                    if len([arg for arg in args if arg.strip() != ""]) == 0:
                        callargs = []
                    else:
                        callargs = [self.resolvestring(a) for a in args]
                    newnode = nodes.Call(ty=words[3], name=name, callargs=callargs)
                    self.registers()[words[0]] = newnode
                elif op == "getelementptr":
                    args = " ".join(words[4:]).split(", ")
                    newnode = nodes.GetElementPtr(
                        [self.resolvestring(idx) for idx in args[2:]]
                    )
                    newnode.ty = args[0]
                    newnode.pre_node = self.resolvestring(args[1])
                    self.registers()[words[0]] = newnode
                elif op == "zext":
                    newnode = nodes.ZeroExtend()
                    newnode.ty = words[6]
                    newnode.pre_node = self.resolvestring(words[3], words[4])
                    self.registers()[words[0]] = newnode
                else:
                    assert False, f"Unknown op {op}"
                newnode.result = words[0]

            elif words[0] == "store":
                newnode = nodes.Store()
                val = self.resolvestring(ty=words[1], val=words[2][:-1])
                newnode.pre_node = val
                newnode.ty = words[3]
                name = words[4][:-1]
                if name in allocs:
                    pt = nodes.StackVar(allocs[name])
                else:
                    pt = nodes.Pointer(ty=words[3], address=name)
                newnode.pointer = pt
                self.addMemEffect(newnode.pointer.address, newnode)

            elif words[0] == "br":
                # print(line)
                args = " ".join(words[1:]).split(", ")
                if len(args) == 1:
                    newnode = nodes.Branch(label=self.resolvestring(args[0]))
                elif len(args) == 3:
                    newnode = nodes.BranchCond(
                        cmp=self.resolvestring(args[0]),
                        label_true=self.resolvestring(args[1]),
                        label_false=self.resolvestring(args[2]),
                    )
                else:
                    assert False, "Wrong num arguments branch"

                # print(self.blocks)
                self.blocks[-1].final = newnode
                # print(
                # "set", self.blocks[-1].label.name, "final to", self.blocks[-1].final
                # )
                # print(self.blocks)

            elif words[0] == "ret":
                newnode = nodes.Ret(
                    ty=words[1], pre_node=self.resolvestring(" ".join(words[1:]))
                )
                # f.ret = newnode
                f.ret = self.blocks[-1]
                f.ret.type = "return"
                f.ret.final = newnode
            elif words[0] == "call":
                #     if words[2] == "asm":
                #         # print(line)
                #         contents = line.split('"')[1]
                #         # print(contents)
                #         newnode = nodes.ASM(contents)
                #         # assert False, "Don't know how to call asm"
                #     else:

                name = words[2].split("(")[0]
                args = " ".join(words[2:]).split("(")[1][:-1].split(",")
                callargs = [self.resolvestring(a) for a in args]
                newnode = nodes.Call(ty=words[1], name=name, callargs=callargs)
                self.sideeffects().append(newnode)
            elif (label := self.stripComments(line)).endswith(":"):
                newname = label[:-1]
                # print(
                #     f"{self.cur_func.name}_%{newname}",
                #     any(
                #         f"{self.cur_func.name}_%{newname}" == b.label.name
                #         for b in self.blocks
                #     ),
                # )
                if newname == "entry" and any(
                    f"{self.cur_func.name}%{newname}" == b.label.name
                    for b in self.blocks
                ):
                    continue
                preds = []
                if "; preds = " in line:
                    preds = line.split("; preds = ")[1].split(", ")
                    preds = [f"{self.cur_func.name}{name}" for name in preds]
                # print("New label", newname, len(self.blocks))
                # self.remove_unused_chains()
                # self.optimize_constant_chains()
                newlabel = nodes.Label(name=f"{self.cur_func.name}%{newname}")
                self.blocks.append(nodes.Block(newlabel, preds))
                # print(self.blocks)
                continue
            else:
                assert False, f"Unknown line `{line}`"

            # if self.cur_label is not None:
            #     newnode.label = self.cur_label
            #     self.cur_label = None
            # print(newnode, "just got label", newnode.label)

        # print()
        # print("before", f.ret)
        # f.ret = self.lower(f.ret)
        # print("after ", f.ret)
        # f.registers = self.registers
        # f.memoryeffects = self.memoryeffects
        f.blocks = self.blocks
        f.allocs = allocs
        # f.chain = self.chain
        self.functions[f.name] = f


#     def construct(self, node):
#         ASM = ""
#         match node:
#             case nodes.Ret():
#                 ASM += self.construct(node.pre_node)
#                 ASM += ";begin epilog\n"
#                 ASM += "STZ R1\n"
#                 ASM += "LD R0 $ebp\n"
#                 ASM += "STSP\n"
#                 ASM += "POP R0\n"
#                 ASM += "ST R0 $ebp\n"
#                 ASM += "LDZ R1\n"
#                 ASM += "RET\n"
#             # case instructions.Add():
#             #     ASM += self.construct(node.op1)
#             #     ASM += "STZ R1\n"
#             #     ASM += self.construct(node.op2)
#             #     ASM += "ADD R1\n"
#             case instructions.CALL():
#                 if len(node.args) > 4:
#                     print(
#                         "Too many instructions to put into registers! More than 4 args not supported yet"
#                     )
#                     exit()
#                 for i in range(len(node.args)):
#                     R = len(node.args) - 1 - i
#                     ASM += self.construct(node.args[i])
#                     if R != 0:
#                         ASM += f"STZ R{R}"
#                 ASM += f"CALL {node.label}\n"
#             case nodes.Load():
#                 if isinstance(const := node.pointer, nodes.Constant):
#                     ASM += f"LDV R0 {const.value}"
#                 else:
#                     print(node.pointer.address)
#                     exit()
#             case nodes.Block():
#                 ASM += node.label.name + ":"
#                 ASM += self.construct(node.final)
#             case _:
#                 print("Failed to construct", type(node))
#                 exit()

#         return ASM

#     def asmPrint(self):
#         # print(self.functions)
#         if "@main" not in self.functions:
#             print("No entrypoint @main found")
#             exit(1)

#         # main = self.functions["@main"]

#         # for k, v in self.registers.items():
#         # print(k, v)
#         # print()
#         # print(main.registers)
#         # print(main.memoryeffects)

#         # for l in main.lines:
#         # print(l)
#         # r = self.lower(main.ret)
#         # print(r)
#         # for name, f in self.functions.items():
#         #     print(name)
#         #     for b in f.blocks:
#         #         print(b.registers)

#         ASM = "LDSP\nST R0 $ebp\nCALL main\nRET\nebp: .db 0xffff\n"
#         for name, f in self.functions.items():
#             ASM += f"{name}:\n"
#             ASM += "LD R0 $ebp\n"
#             ASM += "PSH R0\n"
#             ASM += "LDSP\n"
#             ASM += "ST R0 $ebp\n"
#             ASM += ";prologue concluded\n"
#             ASM += self.construct(self.lower(f.ret))
#         print(ASM)
#         with open("out.ghasm", "w+") as f:
#             f.write(ASM)


# p = parser()
# for f in data["funcs"]:
#     p.parseFunction(f)

# # print(p.blocks)

# p.asmPrint()


# print("\n".join(lines))
