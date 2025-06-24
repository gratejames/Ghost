from enum import Enum

# from os import stat

# from typing import Final


class Node:
    def __init__(self):
        pass


class basetypes(Enum):
    _other = 0
    _void = 1
    _int = 2
    _char = 3


class Type:
    type: basetypes = basetypes._other
    ptr: bool = False

    def __init__(self, _type: str, ptr: bool = False):
        if _type == "void":
            self.type = basetypes._void
        elif _type == "int":
            self.type = basetypes._int
        elif _type == "char":
            self.type = basetypes._char
        self.ptr = ptr

    def __repr__(self):
        name = "other"
        if self.type == basetypes._int:
            name = "int"
        elif self.type == basetypes._char:
            name = "char"
        elif self.type == basetypes._void:
            name = "void"

        if self.ptr:
            name += "*"

        return name


class Statement(Node):
    pass


class Expression(Statement):
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

    def __repr__(self):
        return f"(conditional:{self.conditional} ? {self.expression} : {self.elseExpression})"


class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"id:{self.name}"


class LiteralInteger(Expression):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"int lit:{self.value}"


class LiteralString(Expression):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f"str lit:{self.value}"


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

    def __repr__(self):
        op = "++" if self.direction else "--"
        prefix = op if self.prefix else ""
        suffix = op if not self.prefix else ""
        return f"(increment:{prefix}{self.id}{suffix})"


class Assignment(Expression):
    def __init__(self, id: Identifier, expr: Expression):
        self.id = id
        self.expr = expr

    def __repr__(self):
        return f"(assignment:{self.id} = {self.expr})"


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

    def __repr__(self):
        return f"({self.op}{self.expr_a})"


class biOperation(Expression):
    def __init__(self, op: str, expr_a: Expression, expr_b: Expression):
        self.op = op
        self.expr_a = expr_a
        self.expr_b = expr_b

    def __repr__(self):
        return f"({self.expr_a} {self.op} {self.expr_b})"


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
        self.id = id
        self.expr = expr

    def __repr__(self):
        return f"(declaration assignment:{self._type} {self.id} = {self.expr})"
