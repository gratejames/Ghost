from enum import Enum


class Node:
    def __init__(self):
        pass


class basetypes(Enum):
    _other = 0
    _void = 1
    _int = 2
    _char = 3
    _bool = 4
    _pointer = 5
    _array = 6


class Type:
    type: basetypes

    def __init__(self, _type: str):
        if _type == "void":
            self.type = basetypes._void
        elif _type == "int":
            self.type = basetypes._int
        elif _type == "char":
            self.type = basetypes._char
        elif _type == "bool":
            self.type = basetypes._bool
        else:
            self.type = basetypes._other

    def __repr__(self):
        name = "other"
        if self.type == basetypes._int:
            name = "int"
        elif self.type == basetypes._char:
            name = "char"
        elif self.type == basetypes._bool:
            name = "bool"
        elif self.type == basetypes._void:
            name = "void"

        return str(name)

    def __eq__(self, other):
        if isinstance(other, Type):
            return self.__repr__() == other.__repr__()
        return NotImplemented


class TypeWrapper(Type):
    type: basetypes
    subType: Type


class Pointer(TypeWrapper):
    def __init__(self, _type: Type):
        self.type = basetypes._pointer
        self.subType = _type

    def __repr__(self):
        return f"{self.subType}*"


class Array(Pointer):
    length: int | None

    def __init__(self, _type: Type):
        self.type = basetypes._array
        self.subType = _type
        self.length = None

    def __repr__(self):
        return f"{self.subType}[{self.length}]"


class Statement(Node):
    pass


class Expression(Statement):
    _type: Type = Type("")
    pass


class Include(Statement):
    def __init__(self, file: str):
        self.file = file

    def __repr__(self):
        return f"(include:{self.file})"


class Break(Statement):
    def __repr__(self):
        return "(break)"


class Continue(Statement):
    def __repr__(self):
        return "(continue)"


class Return(Statement):
    def __init__(self, expr: Expression | None):
        self.expr = expr

    def __repr__(self):
        return f"(return {self.expr})"


class _none(Expression):
    pass


class Block(Statement):
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def __repr__(self):
        return "{" + ", ".join(x.__repr__() for x in self.statements) + "}"


def contain(statement: Statement) -> Block:
    if type(statement) is not Block:
        return Block([statement])
    return statement


class Comma(Expression):
    def __init__(self, expr_a: Expression, expr_b: Expression):
        self.expr_a = expr_a
        self.expr_b = expr_b
        self._type = expr_b._type

    def __repr__(self):
        return f"(comma {self.expr_a} {self.expr_b})"


class Conditional(Expression):
    def __init__(
        self,
        conditional: Expression,
        expression: Expression,
        elseExpression: Expression,
    ):
        self.conditional = conditional
        self.expression = expression
        self.elseExpression = elseExpression
        if expression._type == elseExpression._type:
            self._type = expression._type

    def __repr__(self):
        return f"(conditional:{self._type} {self.conditional} ? {self.expression} : {self.elseExpression})"


class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name
        self._type = Type("identifier")

    def __repr__(self):
        return f"id:{self.name}"


class LiteralInteger(Expression):
    def __init__(self, value: int):
        self.value = value
        self._type = Type("int")

    def __repr__(self):
        return f"int lit:{self.value}"


class LiteralString(Expression):
    def __init__(self, value: str):
        self.value = value
        self._type = Pointer(Type("char"))

    def __repr__(self):
        return f"str lit:{self.value}"


class LiteralChar(LiteralInteger):
    def __init__(self, value: str | int):
        self.value = ord(value) if type(value) is str else value
        self._type = Type("char")

    def __repr__(self):
        return f"char lit:'{self.value}'"


class LiteralBool(LiteralInteger):
    def __init__(self, value: bool):
        self.value = value != 0
        self._type = Type("bool")

    def __repr__(self):
        return f"bool lit:'{self.value}'"


class LiteralASM(Expression):
    def __init__(self, value: list[str]):
        self.value = value

    def __repr__(self):
        return f"asm:{len(self.value)} lines"


class Increment(Expression):
    def __init__(self, id: Identifier, prefix: bool, direction: bool):
        self.id = id
        self.prefix = prefix
        self.direction = direction
        self._type = id._type

    def __repr__(self):
        op = "++" if self.direction else "--"
        prefix = op if self.prefix else ""
        suffix = op if not self.prefix else ""
        return f"(increment:{self._type} {prefix}{self.id}{suffix})"


class Assignment(Expression):
    def __init__(self, id: Identifier, expr: Expression):
        self.id = id
        self.expr = expr
        self._type = expr._type

    def __repr__(self):
        return f"(assignment:{self._type} {self.id} = {self.expr})"


class FunctionCall(Expression):
    def __init__(self, id: Identifier, args: list[Expression]):
        self.id = id
        self.args = args

    def __repr__(self):
        return f"(function call:{self.id} {self.args})"


class unOperation(Expression):
    def __init__(self, op: str, expr_a: Expression):
        self.op = op
        self.expr_a = expr_a
        self._type = expr_a._type
        if op == "&":
            self._type = Pointer(self._type)
        elif op == "*" and isinstance(self._type, TypeWrapper):
            self._type = self._type.subType

    def __repr__(self):
        return f"({self.op}{self.expr_a})"


class biOperation(Expression):
    def __init__(self, op: str, expr_a: Expression, expr_b: Expression):
        self.op = op
        self.expr_a = expr_a
        self.expr_b = expr_b
        if op in ["==", ">=", ">", "<=", "<"]:
            self._type = Type("bool")
        elif expr_a._type == expr_b._type:
            self._type = expr_a._type

    def __repr__(self):
        return f"({self.expr_a} {self.op}:{self._type} {self.expr_b})"


class arraySubscript(Identifier):
    def __init__(self, id: Identifier, idx: Expression):
        self.id = id
        self.idx = idx

    def __repr__(self):
        return f"({self.id}[{self.idx}])"


class function_arguments(Node):
    def __init__(self, _type: Type, id: Identifier):
        self._type = _type
        self.id = id

    def __repr__(self):
        return f"(function arg:{self._type} {self.id})"


class Function(Node):
    def __init__(
        self,
        _type: Type,
        id: Identifier,
        args: list[function_arguments],
        statements: list[Statement],
    ):
        self._type = _type
        self.id = id
        self.args = args
        self.statements = statements

    def __repr__(self):
        return f"(function:{self._type} {self.id} {self.args} {self.statements})"


class FunctionPrototype(Node):
    def __init__(self, _type: Type, id: Identifier, args: list[function_arguments]):
        self._type = _type
        self.id = id
        self.args = args

    def __repr__(self):
        return f"(function prototype:{self._type} {self.id} {self.args})"


class If(Statement):
    def __new__(cls, condition: Expression, statement: Statement):
        if type(condition) is LiteralInteger:
            if condition.value != 0:
                return contain(statement)
            else:
                return _none()
        return super(If, cls).__new__(cls)

    def __init__(self, condition: Expression, statement: Statement):
        self.condition = condition
        self.statement = statement

    def __repr__(self):
        return f"(if:{self.condition} {self.statement})"


class IfElse(Statement):
    def __new__(
        cls, condition: Expression, statement: Statement, elseStatement: Statement
    ):
        if type(condition) is LiteralInteger:
            if condition.value == 0:
                return contain(elseStatement)
            else:
                return contain(statement)
        return super(IfElse, cls).__new__(cls)

    def __init__(self, condition, statement, elseStatement):
        self.condition = condition
        self.statement = statement
        self.elseStatement = elseStatement

    def __repr__(self):
        return f"(if else:{self.condition} {self.statement} {self.elseStatement})"


class ForLoop(Statement):
    def __init__(
        self,
        initial: Expression | Statement,
        conditional: Expression,
        post: Expression,
        statement: Statement,
    ):
        self.initial = initial
        self.conditional = conditional
        self.post = post
        self.statement = statement

    def __repr__(self):
        return (
            f"(for loop:{self.initial} {self.conditional} {self.post} {self.statement})"
        )


class While(Statement):
    def __init__(
        self,
        conditional: Expression,
        statement: Statement,
    ):
        self.conditional = conditional
        self.statement = statement

    def __repr__(self):
        return f"(while:{self.conditional} {self.statement})"


class DoWhile(Statement):
    def __init__(
        self,
        conditional: Expression,
        statement: Statement,
    ):
        self.conditional = conditional
        self.statement = statement

    def __repr__(self):
        return f"(do while:{self.conditional} {self.statement})"


class Declaration(Statement):
    def __init__(
        self,
        _type: Type,
        id: Identifier,
    ):
        self._type = _type
        self.id = id

    def __repr__(self):
        return f"(declaration:{self._type} {self.id})"


class DeclarationAssignment(Statement):
    def __init__(
        self,
        _type: Type,
        id: Identifier,
        expr: Expression,
    ):
        self._type = _type
        if _type != expr._type:
            print(
                f"Warning: Assigned expression of type '{expr._type}' to variable of type '{_type}'"
            )
        self.id = id
        self.expr = expr

    def __repr__(self):
        return f"(declaration assignment:{self._type} {self.id} = {self.expr})"
