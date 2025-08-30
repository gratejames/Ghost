import uuid
import immutables
import math
import ast_nodes

# from pathlib import Path

globalASM = ""


def getUID():
    return f"u{str(uuid.uuid4())[:8]}"


class MappedVar:
    _type = ""
    _value = None
    was_read = False
    was_set = False
    added_in_current_context = True
    pref = "?"

    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.pref}({self._type}:{self._value} {int(self.was_read)}{int(self.was_set)}!{self.added_in_current_context})"


class MappedVarLocal(MappedVar):
    pref = "V"

    def __init__(self, _type, stack_index):
        self._type = _type
        self.stack_index = stack_index

    @property
    def stack_index(self):
        return self._value

    @stack_index.setter
    def stack_index(self, value):
        self._value = value


class MappedVarGlobal(MappedVar):
    pref = "G"

    def __init__(self, _type, inital_value):
        self._type = _type
        self.inital_value = inital_value

    @property
    def inital_value(self):
        return self._value

    @inital_value.setter
    def inital_value(self, value):
        self._value = value


class MappedVarFunc(MappedVar):
    pref = "F"

    def __init__(self, _type, arguments):
        self._type = _type
        self.arguments = arguments

    @property
    def arguments(self):
        return self._value

    @arguments.setter
    def arguments(self, value):
        self._value = value


def passctx(var_map):
    vm = {}
    for k, v in var_map.items():
        if isinstance(v, MappedVar):
            v.added_in_current_context = False
        vm[k] = v
    return immutables.Map(vm)


def csrt_expression(state: ast_nodes.Expression, var_map):
    global globalASM
    asm = ""
    if isinstance(lit_int := state, ast_nodes.LiteralInteger):
        asm += f"LD R0 {lit_int.value}\n"
    elif type(lit_str := state) is ast_nodes.LiteralString:
        uid = getUID()
        asm += f"LD R0 {uid}\n"
        globalASM += f'{uid}: .ds "{lit_str.value}"\n.db 0\n'
    elif type(op := state) is ast_nodes.unOperation:
        if op.op == "~":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "NOT R0\n"
        elif op.op == "-":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "NOT R0\n"
            asm += "INC R0\n"
        elif op.op == "!":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "CEZ R0\n"
            asm += f"JMPC not_eq0_{uid}\n"
            asm += "LD R0 0\n"
            asm += f"JMP not_done_{uid}\n"
            asm += f"not_eq0_{uid}:\n"
            asm += "LD R0 1\n"
            asm += f"not_done_{uid}:\n"
        elif op.op == "&":
            if type(op.expr_a) is not ast_nodes.Identifier:
                print("& may only be used on an identifier", op.expr_a)
                exit()
            asm += csrt_recall_id_pointer(op.expr_a.name, var_map)
        elif op.op == "*":
            asm += ";dereference\n"
            asm += csrt_expression(op.expr_a, var_map)
            asm += "DD R0\n"
            asm += "LDD R0\n"
        else:
            print(f"Unknown un-operator: {op.op}")
            exit()
    elif type(op := state) is ast_nodes.biOperation:
        if op.op == "+":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += "ADD R1\n"
        elif op.op == "-":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += "SBR R1\n"
        elif op.op == "&":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += "AND R1\n"
        elif op.op == "^":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += "XOR R1\n"
        elif op.op == "|":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += "OR R1\n"
        elif op.op == "*":
            uid = getUID()
            skip = False
            if type(op.expr_b) is ast_nodes.LiteralInteger:
                n = op.expr_b.value
                if n != 0 and (n & (n - 1)) == 0:
                    k = int(math.log(n, 2))
                    asm += csrt_expression(op.expr_a, var_map)
                    asm += f"SHL R0 {k}\n"
                    skip = True
                else:
                    asm += csrt_expression(op.expr_a, var_map)
                    asm += "STZ R2\n"
                    asm += f"LD R1 {n}\n"
            elif not skip:
                asm += csrt_expression(op.expr_a, var_map)
                asm += "PSH R0\n"
                asm += csrt_expression(op.expr_b, var_map)
                asm += "STZ R1\n"
                asm += "POP R2\n"
            if not skip:
                asm += "LD R0 0\n"
                asm += f"mult_loop_{uid}:\n"
                asm += "CEZ R1\n"
                asm += f"JMPC mult_done_{uid}\n"
                asm += "ADD R2\n"
                asm += "DEC R1\n"
                asm += f"JMP mult_loop_{uid}\n"
                asm += f"mult_done_{uid}:\n"
        elif op.op == "==":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += f"ST R1 $eq_val_{uid}\n"
            asm += f"CE R0 $eq_val_{uid}\n"
            asm += f"JMPC eq_match_{uid}\n"
            asm += "LD R0 0\n"
            asm += f"JMP eq_done_{uid}\n"
            asm += f"eq_val_{uid}:\n"
            asm += ".db 0\n"
            asm += f"eq_match_{uid}:\n"
            asm += "LD R0 1\n"
            asm += f"eq_done_{uid}:\n"
        elif op.op == "==":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += f"ST R1 $eq_val_{uid}\n"
            asm += f"CNE R0 $eq_val_{uid}\n"
            asm += f"JMPC eq_match_{uid}\n"
            asm += "LD R0 0\n"
            asm += f"JMP eq_done_{uid}\n"
            asm += f"eq_val_{uid}:\n"
            asm += ".db 0\n"
            asm += f"eq_match_{uid}:\n"
            asm += "LD R0 1\n"
            asm += f"eq_done_{uid}:\n"
        elif op.op == "<":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += f"ST R1 $eq_val_{uid}\n"
            asm += f"CGT R0 $eq_val_{uid}\n"
            asm += f"JMPC eq_match_{uid}\n"
            asm += "LD R0 0\n"
            asm += f"JMP eq_done_{uid}\n"
            asm += f"eq_val_{uid}:\n"
            asm += ".db 0\n"
            asm += f"eq_match_{uid}:\n"
            asm += "LD R0 1\n"
            asm += f"eq_done_{uid}:\n"
        elif op.op == "<=":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += f"ST R1 $eq_val_{uid}\n"
            asm += f"CLT R0 $eq_val_{uid}\n"
            asm += f"JMPC eq_match_{uid}\n"
            asm += "LD R0 1\n"
            asm += f"JMP eq_done_{uid}\n"
            asm += f"eq_val_{uid}:\n"
            asm += ".db 0\n"
            asm += f"eq_match_{uid}:\n"
            asm += "LD R0 0\n"
            asm += f"eq_done_{uid}:\n"
        elif op.op == ">":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += f"ST R1 $eq_val_{uid}\n"
            asm += f"CLT R0 $eq_val_{uid}\n"
            asm += f"JMPC eq_match_{uid}\n"
            asm += "LD R0 0\n"
            asm += f"JMP eq_done_{uid}\n"
            asm += f"eq_val_{uid}:\n"
            asm += ".db 0\n"
            asm += f"eq_match_{uid}:\n"
            asm += "LD R0 1\n"
            asm += f"eq_done_{uid}:\n"
        elif op.op == ">=":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "POP R1\n"
            asm += f"ST R1 $eq_val_{uid}\n"
            asm += f"CGT R0 $eq_val_{uid}\n"
            asm += f"JMPC eq_match_{uid}\n"
            asm += "LD R0 1\n"
            asm += f"JMP eq_done_{uid}\n"
            asm += f"eq_val_{uid}:\n"
            asm += ".db 0\n"
            asm += f"eq_match_{uid}:\n"
            asm += "LD R0 0\n"
            asm += f"eq_done_{uid}:\n"
        elif op.op == "<<":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "STZ R1\n"
            asm += "POP R0\n"
            asm += "SHL R1\n"
        elif op.op == ">>":
            asm += csrt_expression(op.expr_a, var_map)
            asm += "PSH R0\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "STZ R1\n"
            asm += "POP R0\n"
            asm += "SHR R1\n"
        elif op.op == "&&":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "CEZ R0\n"
            asm += f"JMPC and_false_{uid}\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "CEZ R0\n"
            asm += f"JMPC and_false_{uid}\n"
            asm += "LD R0 1\n"
            asm += f"JMP and_done_{uid}\n"
            asm += f"and_false_{uid}:\n"
            asm += "LD R0 0\n"
            asm += f"and_done_{uid}:\n"
        elif op.op == "||":
            uid = getUID()
            asm += csrt_expression(op.expr_a, var_map)
            asm += "CNZ R0\n"
            asm += f"JMPC or_true_{uid}\n"
            asm += csrt_expression(op.expr_b, var_map)
            asm += "CNZ R0\n"
            asm += f"JMPC or_true_{uid}\n"
            asm += "LD R0 0\n"
            asm += f"JMP or_done_{uid}\n"
            asm += f"or_true_{uid}:\n"
            asm += "LD R0 1\n"
            asm += f"or_done_{uid}:\n"
        else:
            print(f"Unknown bi-operator: {op.op}")
            exit()
    elif type(assign := state) is ast_nodes.Assignment:
        asm += csrt_expression(assign.expr, var_map)
        asm += csrt_assign_identifier(assign.id, var_map)
    elif type(ident := state) is ast_nodes.Identifier:
        asm += csrt_recall_identifier(ident.name, var_map)
    elif type(comma := state) is ast_nodes.Comma:
        asm += csrt_expression(comma.expr_a, var_map)
        asm += csrt_expression(comma.expr_b, var_map)
    elif type(incr := state) is ast_nodes.Increment:
        if incr.prefix:
            # Increment
            # Store
            # Return
            asm += ";pre increment identifier\n"
            asm += csrt_recall_identifier(incr.id.name, var_map)
            asm += "INC R0\n" if incr.direction else "DEC R0\n"
            asm += "STD R0\n"
        else:
            # Return
            # Increment
            # Store
            asm += ";post increment identifier\n"
            asm += csrt_recall_identifier(incr.id.name, var_map)
            asm += "STZ R1\n"
            asm += "INC R0\n" if incr.direction else "DEC R0\n"
            asm += "STD R0\n"
            asm += "LDZ R1\n"
    elif type(cond := state) is ast_nodes.Conditional:
        uid = getUID()
        asm += csrt_expression(cond.conditional, var_map)
        asm += "CEZ R0\n"
        asm += f"JMPC if_else_false_{uid}\n"
        asm += csrt_expression(cond.expression, var_map)
        asm += f"JMP if_else_done_{uid}\n"
        asm += f"if_else_false_{uid}:\n"
        asm += csrt_expression(cond.elseExpression, var_map)
        asm += f"if_else_done_{uid}:\n"
    elif type(func := state) is ast_nodes.FunctionCall:
        if func.id.name not in var_map:
            # print(f"Function not found: {func.id.name}. (in {var_map})")
            print(f"Function not found: {func.id.name}.")
            exit()
        var = var_map[func.id.name]
        if type(var) is not MappedVarFunc:
            print(f"{func.id.name} is not a function.")
            exit()
        var.was_read = True
        for arg in func.args[::-1]:
            asm += ";function call\n"
            if isinstance(arg, ast_nodes.LiteralInteger):
                asm += f"LD R0 {arg.value}\n"
                asm += "PSH R0\n"
            else:
                asm += csrt_expression(arg, var_map)
                asm += "PSH R0\n"
        asm += f"CALL {func.id.name}\n"
        asm += "STZ R1\n"
        asm += "LDSP\n"
        asm += f"ADD R0 {len(func.args)}\n"
        asm += "STSP\n"
        asm += "LDZ R1\n"
    elif type(subscript := state) is ast_nodes.arraySubscript:
        # if type(expr.id) is not ast_nodes.Identifier:
        #     print("& may only be used on an identifier", op.expr_a)
        #     exit()
        # asm += csrt_recall_id_pointer(expr.id.name, var_map)
        # asm += f"ADD R0 {expr.idx}"
        # asm += csrt_expression(
        #     ast_nodes.biOperation(
        #         "+", ast_nodes.unOperation("*", subscript.id), subscript.idx
        #     ),
        #     var_map,
        # )

        asm += ";dereference\n"
        asm += csrt_expression(subscript.id, var_map)
        asm += "PSH R0\n"
        asm += csrt_expression(subscript.idx, var_map)
        asm += "POP R1\n"
        asm += "SBR R1\n"
        asm += "DD R0\n"
        asm += "LDD R0\n"
        # uid = getUID()
        # asm += f"LD R0 {uid}\n"
        # globalASM += f'{uid}: .ds "{lit_str.value}"\n.db 0\n'
    elif type(sub_asm := state) is ast_nodes.LiteralASM:
        asm += "\n".join(sub_asm.value)
    else:
        print(f"Unknown expression: {state}")
        exit()
    return asm


def csrt_assign_identifier(
    id: ast_nodes.Identifier | ast_nodes.arraySubscript, var_map
):
    if type(id) is ast_nodes.arraySubscript:
        var_id = id.id.name

        asm = ""
        if var_id not in var_map:
            print(f"Unknown identifier: {var_id}")
            exit()
        var = var_map[var_id]
        if type(var) is MappedVarLocal:
            stack_index = var.stack_index
            asm += ";assign identifier\n"
            asm += "PSH R0\n"
            asm += "LD R1 $ebp\n"
            asm += f"SUB R1 {-stack_index}\n"
            asm += "PSH R1\n"
            asm += csrt_expression(id.idx, var_map)
            asm += "POP R1\n"
            asm += "SBR R1\n"
            asm += "DD R0\n"
            asm += "POP R0\n"
            asm += "STD R0\n"
        # elif type(var) is MappedVarGlobal: # TODO
        else:
            print("Unknown variable type", var_id)
            exit()

        var.was_set = True
        return asm
    else:
        var_id = id.name

        asm = ""
        if var_id not in var_map:
            print(f"Unknown identifier: {var_id}")
            exit()
        var = var_map[var_id]
        if type(var) is MappedVarLocal:
            stack_index = var.stack_index
            asm += ";assign identifier\n"
            asm += "LD R1 $ebp\n"
            asm += f"SUB R1 {-stack_index}\n"
            asm += "DD R1\n"
            asm += "STD R0\n"
        elif type(var) is MappedVarGlobal:
            asm += f"ST R0 ${var_id}"
        else:
            print("Unknown variable type", var_id)
            exit()

        var.was_set = True
        return asm


def csrt_recall_id_pointer(var_id: str, var_map):
    asm = ""
    if var_id not in var_map:
        print(f"Unknown identifier: {var_id}")
        exit()
    var = var_map[var_id]
    if type(var) is MappedVarLocal:
        stack_index = var.stack_index
        asm += ";recall identifier pointer\n"
        asm += "LD R0 $ebp\n"
        asm += (
            f"SUB R0 {-stack_index}\n"
            if stack_index < 0
            else f"ADD R0 {stack_index}\n"
            if stack_index > 0
            else ""
        )
    elif type(var) is MappedVarGlobal:
        asm += f"LD R0 {var_id}\n"
    else:
        print("Unknown variable type", var_id)
        exit()

    var.was_read = True

    return asm


def csrt_recall_identifier(var_id: str, var_map):
    asm = ""
    if var_id not in var_map:
        print(f"Unknown identifier: {var_id}")
        exit()
    var = var_map[var_id]
    if type(var) is MappedVarLocal:
        stack_index = var.stack_index
        asm += ";recall identifier\n"
        asm += "LD R0 $ebp\n"
        asm += (
            f"SUB R0 {-stack_index}\n"
            if stack_index < 0
            else f"ADD R0 {stack_index}\n"
            if stack_index > 0
            else ""
        )
        asm += "DD R0\n"
        asm += "LDD R0\n"
    elif type(var) is MappedVarGlobal:
        asm += f"LD R0 ${var_id}\n"
    else:
        print("Unknown variable type", var_id)
        exit()

    var.was_read = True

    return asm


def csrt_statement(
    state: ast_nodes.Statement, var_map, stack_index: int, current_scope: tuple
):
    asm = ""
    if type(ret := state) is ast_nodes.Return:
        if ret.expr is not None:
            asm += csrt_expression(ret.expr, var_map)
        asm += ";begin epilog\n"
        if ret.expr is not None:
            asm += "STZ R1\n"
        asm += "LD R0 $ebp\n"
        asm += "STSP\n"
        asm += "POP R0\n"
        asm += "ST R0 $ebp\n"
        if ret.expr is not None:
            asm += "LDZ R1\n"
        asm += "RET\n"
    elif type(decl := state) is ast_nodes.DeclarationAssignment:
        if decl.id.name in current_scope:
            print(f"Already declared: {decl.id.name}")
            exit()
        if isinstance(decl._type, ast_nodes.Array):
            items = []
            if decl._type.length is None:
                if isinstance(decl.expr, ast_nodes.LiteralString):
                    decl._type.length = len(decl.expr.value) + 1
                    items += [f"'{x}'" for x in decl.expr.value] + [0]
                else:
                    print("Can only guess length of strings.")
                    exit()
            asm += ";declare array\n"
            asm += "LDSP\n"
            for i in range(decl._type.length):
                # print(i, len(items), items)
                val = 0 if i > len(items) else items[i]
                asm += f"LD R1 {val}\n"
                asm += "PSH R1\n"
            asm += "PSH R0\n"  # Add pointer to array in stack
            stack_index -= decl._type.length
            var = MappedVarLocal(decl._type, stack_index)
            var.was_set = True
            var_map = var_map.set(decl.id.name, var)
            stack_index -= 1
        elif (
            isinstance(decl._type, ast_nodes.Pointer)
            or decl._type.type == ast_nodes.basetypes._int
        ):
            current_scope += (decl.id.name,)
            asm += ";declare and assign identifier\n"
            asm += csrt_expression(decl.expr, var_map)
            asm += "PSH R0\n"
            var = MappedVarLocal(decl._type, stack_index)
            var.was_set = True
            var_map = var_map.set(decl.id.name, var)
            stack_index -= 1
        else:
            print(f"Unknown type: {decl._type}")
            exit(1)
    elif type(decl := state) is ast_nodes.Declaration:
        if decl.id.name in current_scope:
            print(f"Already declared: {decl.id.name}")
            exit(1)
        if isinstance(decl._type, ast_nodes.Array):
            if decl._type.length is None:
                print("Can't guess at array length in definition.")
                exit()
            asm += ";declare array\n"
            asm += "LDSP\n"
            asm += "LD R1 0\n"
            for i in range(decl._type.length):
                asm += "PSH R1\n"
            asm += "PSH R0\n"  # Add pointer to array in stack
            stack_index -= decl._type.length
            var_map = var_map.set(decl.id.name, MappedVarLocal(decl._type, stack_index))
            stack_index -= 1
        elif (
            isinstance(decl._type, ast_nodes.Pointer)
            or decl._type.type == ast_nodes.basetypes._int
        ):
            current_scope += (decl.id.name,)
            asm += ";declare identifier\n"
            asm += "LD R0 0\n"
            asm += "PSH R0\n"
            var_map = var_map.set(decl.id.name, MappedVarLocal(decl._type, stack_index))
            stack_index -= 1
        else:
            print(f"Unknown type: {decl} {decl._type} {ast_nodes.basetypes._int}")
            exit()
    elif type(_if := state) is ast_nodes.If:
        uid = getUID()
        asm += csrt_expression(_if.condition, var_map)
        asm += "CEZ R0\n"
        asm += f"JMPC if_skip_{uid}\n"
        asm += csrt_statement(_if.statement, var_map, stack_index, current_scope)[0]
        asm += f"if_skip_{uid}:\n"
    elif type(_if_else := state) is ast_nodes.IfElse:
        uid = getUID()
        asm += csrt_expression(_if_else.condition, var_map)
        asm += "CEZ R0\n"
        asm += f"JMPC if_else_false_{uid}\n"
        asm += csrt_statement(_if_else.statement, var_map, stack_index, current_scope)[
            0
        ]
        asm += f"JMP if_else_done_{uid}\n"
        asm += f"if_else_false_{uid}:\n"
        asm += csrt_statement(
            _if_else.elseStatement, var_map, stack_index, current_scope
        )[0]
        asm += f"if_else_done_{uid}:\n"
    elif type(_while := state) is ast_nodes.While:
        uid = getUID()
        var_map = var_map.set("__continue_target", f"while_start_{uid}")
        var_map = var_map.set("__break_target", f"while_done_{uid}")
        asm += f"while_start_{uid}:\n"
        asm += csrt_expression(_while.conditional, var_map)
        asm += "CEZ R0\n"
        asm += f"JMPC while_done_{uid}\n"
        asm += csrt_statement(_while.statement, var_map, stack_index, current_scope)[0]
        asm += f"JMP while_start_{uid}\n"
        asm += f"while_done_{uid}:\n"
    elif type(do_while := state) is ast_nodes.DoWhile:
        uid = getUID()
        var_map = var_map.set("__continue_target", f"do_while_start_{uid}")
        var_map = var_map.set("__break_target", f"do_while___break_target_{uid}")
        asm += f"do_while_start_{uid}:\n"
        asm += csrt_statement(do_while.statement, var_map, stack_index, current_scope)[
            0
        ]
        asm += csrt_expression(do_while.conditional, var_map)
        asm += "CNZ R0\n"
        asm += f"JMPC do_while_start_{uid}\n"
        asm += f"JMPC do_while___break_target_{uid}\n"
    elif type(do_while := state) is ast_nodes.ForLoop:
        uid = getUID()
        new_asm, var_map, stack_index, current_scope = csrt_statement(
            do_while.initial, var_map, stack_index, current_scope
        )
        var_map = var_map.set("__continue_target", f"for___continue_target_{uid}")
        var_map = var_map.set("__break_target", f"for_loop_done_{uid}")
        asm = ""
        asm += new_asm
        asm += f"for_loop_condition_{uid}:\n"
        asm += csrt_expression(do_while.conditional, var_map)
        asm += "CEZ R0\n"
        asm += f"JMPC for_loop_done_{uid}\n"

        asm += csrt_statement(do_while.statement, var_map, stack_index, current_scope)[
            0
        ]
        asm += f"for___continue_target_{uid}:\n"
        asm += csrt_statement(do_while.post, var_map, stack_index, current_scope)[0]
        asm += f"JMP for_loop_condition_{uid}\n"

        asm += f"for_loop_done_{uid}:\n"
    elif type(block := state) is ast_nodes.Block:
        asm += cstr_block(block.statements, var_map, stack_index)
    elif type(state) is ast_nodes.Continue:
        if var_map["__continue_target"] == 0:
            print("Syntax error: Continue may only be used in a loop.")
            exit()
        asm += f"JMP {var_map['__continue_target']}\n"
    elif type(state) is ast_nodes.Break:
        if var_map["__break_target"] == 0:
            print("Syntax error: Break may only be used in a loop.")
            exit()
        asm += f"JMP {var_map['__break_target']}\n"
    elif type(state) is ast_nodes._none:
        pass
    else:
        asm += csrt_expression(state, var_map)
        # print(f"Unknown statement: {state[0]}")
        # exit()
    return (asm, var_map, stack_index, current_scope)


def cstr_block(states: list[ast_nodes.Statement], var_map, stack_index):
    asm = ""
    current_scope = ()
    for state in states:
        if (
            type(state) is ast_nodes.Declaration
            or type(state) is ast_nodes.DeclarationAssignment
        ):
            new_asm, var_map, stack_index, current_scope = csrt_statement(
                state, var_map, stack_index, current_scope
            )
            asm += new_asm
        else:
            asm += csrt_statement(state, var_map, stack_index, current_scope)[0]

    if len(asm) < 1 or asm.split("\n")[-2] != "RET":
        for i in range(len(current_scope)):
            asm += "POP R0\n"
    return asm


def csrt_function(functionStruct: ast_nodes.Function, var_map: immutables.Map):
    var_map = passctx(var_map)
    asm = f"{functionStruct.id.name}:\n"
    asm += "LD R0 $ebp\n"
    asm += "PSH R0\n"
    asm += "LDSP\n"
    asm += "ST R0 $ebp\n"
    asm += ";prologue concluded\n"
    f = MappedVarFunc(functionStruct._type, functionStruct.args)
    f.was_set = True
    var_map = var_map.set(functionStruct.id.name, f)
    stack_index = 3  # Return address and ebp are above
    for arg in functionStruct.args:
        a_type = arg._type
        a_id = arg.id.name
        if isinstance(a_type, ast_nodes.Pointer):
            var = MappedVarLocal(arg._type, stack_index)
            var.was_set = True
            var_map = var_map.set(a_id, var)
            stack_index += 1
        elif a_type.type == ast_nodes.basetypes._int:  # TODO HANDLE ARRAY
            # if a_id in current_scope:
            #     print(f"Already declared: {a_id}")
            #     exit()
            # current_scope += (a_id,)
            # asm += ";load argument identifier\n"
            # asm += "LD R0 0\n"
            # asm += "PSH R0\n"
            var = MappedVarLocal(arg._type, stack_index)
            var.was_set = True
            var_map = var_map.set(a_id, var)
            stack_index += 1
        else:
            print(f"Unknown type: {a_type}")
            exit()

    # print("FUNC")
    # for k, v in var_map.items():
    #     if not isinstance(v, MappedVar):
    #         continue
    #     if v.added_in_current_context:
    #         print(k, v)

    asm += cstr_block(functionStruct.statements, var_map, 0)
    if asm.split("\n")[-2] != "RET":
        asm += ";begin auto-epilog\n"
        asm += "LD R0 0\n"
        asm += "STZ R1\n"
        asm += "LD R0 $ebp\n"
        asm += "STSP\n"
        asm += "POP R0\n"
        asm += "ST R0 $ebp\n"
        asm += "LDZ R1\n"
        asm += "RET\n"
    return asm


def construct(AST: list[ast_nodes.Node], fs=False) -> str | int:
    asm = ""
    var_map = immutables.Map(__continue_target=0, __break_target=0)
    for mainNode in AST:
        if type(mainNode) is ast_nodes.Include:
            # print("Including ", mainNode.file)
            asm += f"#INC {mainNode.file}\n"
        elif type(mainNode) is ast_nodes.Function:
            # if mainNode.id.name == "main":
            #     if mainNode._type.type != ast_nodes.types._int:
            #         print("Main function must return int")
            #         exit()
            new_asm = csrt_function(mainNode, var_map)
            asm += new_asm
            f = MappedVarFunc(mainNode._type, mainNode.args)
            f.was_set = True
            var_map = var_map.set(mainNode.id.name, f)
        elif type(mainNode) is ast_nodes.FunctionPrototype:
            # if mainNode.id.name == "main":
            #     if mainNode._type.type != ast_nodes.types._int:
            #         print("Main function must return int")
            #         exit()
            var_map = var_map.set(
                mainNode.id.name, MappedVarFunc(mainNode._type, mainNode.args)
            )
        elif type(mainNode) is ast_nodes.Declaration:
            _id = mainNode.id.name
            if _id in var_map:
                var = var_map[_id]
                if type(var) is not MappedVarGlobal:
                    print("Is not a global var", mainNode)
                    exit()
            else:
                asm += f"{_id}: .db 0\n"
                var_map = var_map.set(
                    mainNode.id.name, MappedVarGlobal(mainNode._type, None)
                )
        elif type(mainNode) is ast_nodes.DeclarationAssignment:
            val = mainNode.expr
            if type(val) is ast_nodes.LiteralInteger:
                val = val.value
            else:
                print("Compound root-declarations not supported", mainNode)
                exit()
            val_asm = f"{mainNode.id.name}: .db {val}\n"
            if mainNode.id.name in var_map:
                var = var_map[mainNode.id.name]
                if type(var) is not MappedVarGlobal:
                    print("Already reserved, but not a global variable", mainNode)
                    exit()
                if var.inital_value is None:
                    asm = asm.replace(f"{mainNode.id.name}: .db 0\n", val_asm)
                else:
                    print("Already declared", mainNode)
                    exit()
            gv = MappedVarGlobal(mainNode._type, val)
            gv.was_set = True
            var_map = var_map.set(mainNode.id.name, gv)
        else:
            print("Constructor unexpected AST item", mainNode)
            exit()
        # print(var_map)

    if "main" not in var_map:
        print("No main function")
        exit()
    main_var = var_map["main"]
    if type(main_var) is not MappedVarFunc:
        print("main must be a function", main_var)
        exit()
    if main_var._type.type != ast_nodes.basetypes._int:
        print("main must return integer", main_var, main_var._type is int)
        exit()
    if len(main_var.arguments) != 0 and (
        len(main_var.arguments) != 1
        or main_var.arguments[0]._type.type != ast_nodes.basetypes._int
    ):
        print("main must take one int as arg", main_var)
        exit()
    main_var.was_read = True

    # for k, v in var_map.items():
    #     if isinstance(v, MappedVar):
    #         print(k, v)

    end = "RET" if fs else "DBG R0\nHLT"
    asm = (
        f"LDSP\nST R0 $ebp\nCALL main\n{end}\nebp: .db 0xffff\n"
        + asm
        + "\n"
        + globalASM
    )
    return asm


if __name__ == "__main__":
    from tokenizer import tokenize, token
    from my_ast import ast_head
    from pathlib import Path

    file = "test.g"
    with open(file, "r") as f:
        fileContents: str = f.read()

    tokens: list[token] = tokenize(fileContents, Path(file))

    # print(tokens)
    AST: list[ast_nodes.Node] = ast_head(tokens)
    if AST == []:
        exit()
    print(AST)
    assembly = str(construct(AST))

    with open("test.ghasm", "w+") as f:
        f.write(assembly)
