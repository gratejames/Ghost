import nodes


class printer:
    def __init__(self, arr, register_translation, globals):
        self.arr = arr
        self.reg_trans = register_translation
        self.globals = globals

    def getname(self, name):
        return self.function.name + name

    def moveRegister(self, start, end):
        asm = ""
        if start != end:
            if start != "R0":
                asm += f"LDZ {start}\n"
            if end != "R0":
                asm += f"STZ {end}\n"
        return asm

    def translate_instruction(self, node):
        match node:
            case nodes.Function():
                self.function = node
                asm = f"{node.name}:\n"
                asm += "PSH R1\n"
                asm += "PSH R2\n"
                asm += "PSH R3\n"
                asm += "ST R0 $r0_hold\n"
                asm += "LD R0 $ebp\n"
                asm += "PSH R0\n"
                asm += "LDSP\n"
                asm += "ST R0 $ebp\n"
                asm += "LD R0 $r0_hold\n"
                asm += ";prologue concluded\n"
            case nodes.Label():
                asm = f"{node.name}:\n"
            case nodes.lateAlloc():
                asm = f";alloc identifier {self.getname(node.register)}\n"
                asm += "PSH R0\n"
            case nodes.Load():
                if isinstance(node.pointer, nodes.StackVar):
                    r_out = self.reg_trans[self.getname(node.result)]
                    asm = f";recall identifier {node.result}\n"
                    # asm += "PSH R0\n"
                    asm += "LD R0 $ebp\n"
                    asm += f"SUB R0 {node.pointer.address}\n"
                    asm += "DD R0\n"
                    asm += f"LDD {r_out}\n"
                    # asm += f"STZ {r_out}\n"
                    # asm += "POP R0\n"
                else:
                    print("Don't know how to load this pointer type!", node.pointer)
                    exit()
            case nodes.Store():
                if isinstance(node.pointer, nodes.StackVar):
                    if isinstance(node.pre_node, nodes.RegisterReference):
                        asm = f";assign identifier {node.pointer}\n"
                        r_in = self.reg_trans[self.getname(node.pre_node.name)]
                        if r_in == "R0":
                            asm += "ST R0 $r0_hold\n"
                        asm += "LD R0 $ebp\n"
                        asm += f"SUB R0 {node.pointer.address}\n"
                        asm += "DD R0\n"
                        if r_in == "R0":
                            asm += "LD R0 $r0_hold\n"
                        asm += f"STD {r_in}\n"
                    elif isinstance(node.pre_node, nodes.Constant):
                        asm = f";assign identifier {node.pointer}\n"
                        asm += "LD R0 $ebp\n"
                        asm += f"SUB R0 {node.pointer.address}\n"
                        asm += "DD R0\n"
                        asm += f"STD {node.pre_node.value}\n"
                    else:
                        print("Don't know how to store this value type!", node.pre_node)
                        exit()
                else:
                    print("Don't know how to store to this pointer type!", node.pointer)
                    exit()
            case nodes.BiOp():
                op = node.op.upper()
                if op not in ["ADD", "SUB"]:
                    print("Don't know biop", op)
                    exit()
                if isinstance(node.op1, nodes.RegisterReference):
                    r_in = self.reg_trans[self.getname(node.op1.name)]
                    if isinstance(node.op2, nodes.Constant):
                        asm = f"{op} {r_in} {node.op2.value}\n"
                        done_r = r_in
                    elif isinstance(node.op2, nodes.RegisterReference):
                        r_op2 = self.reg_trans[self.getname(node.op2.name)]
                        asm = f"LDZ {r_in}\n"
                        asm += f"{op} {r_op2}\n"
                        done_r = "R0"
                    else:
                        print("Don't know how to biop register to", node.op2)
                        exit()
                else:
                    print("Not sure how to biop", node.op1)
                    exit()

                out_r = self.reg_trans[self.getname(node.result)]
                asm += self.moveRegister(done_r, out_r)
            case nodes.Icmp():
                if node.op == "eq":
                    if isinstance(node.op1, nodes.RegisterReference):
                        r_in = self.reg_trans[self.getname(node.op1.name)]
                        if isinstance(node.op2, nodes.Constant):
                            if int(node.op2.value) == 0:
                                asm = f"CEZ {r_in}\n"
                            else:
                                asm = f"CE {r_in} {node.op2.value}\n"
                        elif isinstance(node.op2, nodes.RegisterReference):
                            r_op2 = self.reg_trans[self.getname(node.op2.name)]
                            asm = f"LDZ {r_in}\n"
                            asm += f"XOR {r_op2}\n"
                            asm += "CEZ RO\n"
                        else:
                            print("Not sure how to Icmp Register to", node.op2)
                            exit()
                    else:
                        print("Not sure how to Icmp", node.op1)
                        exit()
                else:
                    print("Unknown comparison operation:", node.op)
                    exit()
            case nodes.Call():
                asm = ""
                asm += f";Call {node.name}\n"
                # Make sure R0 is free until end, as it is used for setting up other vars
                for i, a in enumerate(node.callargs[::-1]):
                    start_r = self.reg_trans[self.getname(a.name)]
                    dest_r = f"R{i}"
                    # print(i,a.name,start_r,dest_r)
                    asm += self.moveRegister(start_r, dest_r)
                asm += f"CALL {node.name}\n"
                r_out = self.reg_trans[self.getname(node.result)]
                asm += self.moveRegister("R0", r_out)

                # print(asm)
                # exit()
            case nodes.Ret():
                asm = ";return\n"
                if isinstance(node.pre_node, nodes.RegisterReference):
                    r_done = self.reg_trans[self.getname(node.pre_node.name)]
                    if r_done == "R0":
                        asm += "STZ R1"
                        r_done = "R1"
                    asm += "LD R0 $ebp\n"
                    asm += "STSP\n"
                    asm += "POP R0\n"
                    asm += "ST R0 $ebp\n"
                    asm += self.moveRegister(r_done, "R0")
                    asm += "POP R3\n"
                    asm += "POP R2\n"
                    asm += "POP R1\n"
                else:
                    print("Don't know how to return", node.pre_node)
                    exit()
                asm += "RET\n"
            case nodes.BranchCond():
                asm = f"JMPC {self.getname(node.label_true.name)}\n"
                asm += f"JMP {self.getname(node.label_false.name)}\n"
            case nodes.Branch():
                asm = f"JMP {self.getname(node.label.name)}\n"
            case nodes.FunctionDefArgument():
                return ""
            case _:
                print("Can't translate into instruction:", str(type(node)), node)
                exit()
                # return "!NO TRANS! " + str(node) + "\n"

        return asm

    def out(self):
        end = "RET" if False else "DBG R0\nHLT"
        ASMout = (
            f"LDSP\nST R0 $ebp\nCALL @main\n{end}\nebp: .db 0xffff\nr0_hold: .db 0\n"
        )
        for name, val in self.globals:
            ASMout += f"{name}: "
            if type(val) is int:
                ASMout += f".db {val}\n"
            elif type(val) is str:
                ASMout += '.ds "'
                ASMout += val.replace("\\", '"\n.db 0x"') + '"\n'
        print(ASMout)

        for node in self.arr:
            ASMout += self.translate_instruction(node)
        return ASMout
