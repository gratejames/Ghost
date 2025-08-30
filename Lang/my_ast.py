from tokenizer import token
import ast_nodes
from pathlib import Path
import uuid
import copy


def ast_type(tokens: list[token]) -> ast_nodes.Type | None:
    _type = tokens.pop(0)
    if _type.type != "type" or type(_type.contents) is not str:
        print("Expected a type", _type)
        return None

    t = ast_nodes.Type(_type.contents)

    nextTok = ast_peek(tokens)
    if nextTok.type == "operator" and nextTok.contents == "*":
        tokens.pop(0)
        return ast_nodes.Pointer(t)

    return t


def ast_identifier(_id: token) -> ast_nodes.Identifier | None:
    if (
        _id.type != "identifier"
        or type(_id.contents) is not str
        or len(_id.contents) == 0
    ):
        print("Expected an identifier", _id)
        return None
    if not _id.contents[0].isalpha():
        print("Identifier must start with a letter", _id)
        return None
    return ast_nodes.Identifier(_id.contents)


def ast_peek(tokens: list[token], i: int = 0) -> token:
    if len(tokens) > i:
        return tokens[i]
    print("Unexpected EOF")
    exit()


def op_invert(operand):
    return int(
        "".join(["1" if x == "0" else "0" for x in format(operand, "#018b")[2:]]), 2
    )


def ast_operation(
    operation_type: str,
    operand_a: ast_nodes.Expression,
    operand_b: ast_nodes.Expression | None = None,
) -> ast_nodes.Expression:
    if operand_b is None:
        if isinstance(operand_a, ast_nodes.LiteralInteger):
            match operation_type:
                case "-":
                    return ast_nodes.LiteralInteger(-operand_a.value)
                case "~":
                    return ast_nodes.LiteralInteger(
                        op_invert(operand_a.value),
                    )
                case "!":
                    return ast_nodes.LiteralInteger(int(operand_a.value == 0))
        return ast_nodes.unOperation(operation_type, operand_a)
    else:
        if isinstance(operand_a, ast_nodes.LiteralInteger) and operation_type in [
            "*",
            "+",
        ]:
            temp = operand_a
            operand_a = operand_b
            operand_b = temp

        if isinstance(operand_b, ast_nodes.LiteralInteger) and operation_type == "*":
            if operand_b.value == 0:
                return ast_nodes.LiteralInteger(0)
            if operand_b.value == 1:
                return operand_a

        if isinstance(operand_b, ast_nodes.LiteralInteger) and operation_type in [
            "+",
            "-",
            "|",
            "^",
        ]:
            if operand_b.value == 0:
                return operand_a

        if isinstance(operand_b, ast_nodes.LiteralInteger) and operation_type == "&":
            if operand_b.value == 0xFFFF:
                return operand_a

        if operation_type == "&&" and (
            (isinstance(operand_a, ast_nodes.LiteralInteger) and operand_a.value == 0)
            or (
                isinstance(operand_b, ast_nodes.LiteralInteger) and operand_b.value == 0
            )
        ):
            return ast_nodes.LiteralInteger(0)

        if operation_type == "||" and (
            (isinstance(operand_a, ast_nodes.LiteralInteger) and operand_a.value != 0)
            or (
                isinstance(operand_b, ast_nodes.LiteralInteger) and operand_b.value != 0
            )
        ):
            return ast_nodes.LiteralInteger(1)

        if isinstance(operand_a, ast_nodes.LiteralInteger) and isinstance(
            operand_b, ast_nodes.LiteralInteger
        ):
            match operation_type:
                case "*":
                    return ast_nodes.LiteralInteger(operand_a.value * operand_b.value)
                case "+":
                    return ast_nodes.LiteralInteger(operand_a.value + operand_b.value)
                case "-":
                    return ast_nodes.LiteralInteger(operand_a.value - operand_b.value)
                case "<<":
                    return ast_nodes.LiteralInteger(operand_a.value << operand_b.value)
                case ">>":
                    return ast_nodes.LiteralInteger(operand_a.value >> operand_b.value)
                case "&":
                    return ast_nodes.LiteralInteger(operand_a.value & operand_b.value)
                case "|":
                    return ast_nodes.LiteralInteger(operand_a.value | operand_b.value)
                case "^":
                    return ast_nodes.LiteralInteger(operand_a.value ^ operand_b.value)

        return ast_nodes.biOperation(operation_type, operand_a, operand_b)


def ast_arguments(tokens: list[token]) -> list[ast_nodes.function_arguments] | None:
    arguments: list[ast_nodes.function_arguments] = []
    o_paren = tokens.pop(0)
    if o_paren.type != "open paren":
        print("Arguments must start with a paren", o_paren)
        return None
    while True:
        # pointer = False
        nextTok = ast_peek(tokens)
        if nextTok.type == "close paren":
            tokens.pop(0)
            break

        a_type = ast_type(tokens)
        if a_type is None:
            return None
        # if a_type.type != "type":
        #     if a_type.type == "open brace":
        #         print("Syntax error: missing close paren?", f"Line {a_type.line}")
        #         return None
        #     print("Arguments must start with a type", a_type)
        #     return None
        # a_name = tokens.pop(0)
        # if a_name.type == "operator" and a_name.contents == "*":
        #     pointer = True
        #     a_name = tokens.pop(0)
        if a_type.type is ast_nodes.basetypes._void:
            a_name = ast_nodes.Identifier("Void")
        else:
            a_name = ast_identifier(tok := tokens.pop(0))
            if a_name is None:
                print("Arguments type must be followed by identifier", tok)
                return None
        arguments.append(ast_nodes.function_arguments(a_type, a_name))

        peekTok = ast_peek(tokens)
        if peekTok.type == "operator" and peekTok.contents == ",":
            tokens.pop(0)
            continue
        elif peekTok.type == "close paren":
            continue
        else:
            print("Unknown argument token", peekTok)
            return None

    if any(arg._type.type is ast_nodes.basetypes._void for arg in arguments):
        if len(arguments) != 1:
            print("If 'void' is the argument, it must stand alone.")
            return None
        arguments = []

    return arguments


def ast_call_arguments(
    tokens: list[token],
) -> list[ast_nodes.Expression] | None:
    arguments: list[ast_nodes.Expression] = []
    while True:
        peekTok = ast_peek(tokens)
        if peekTok.type == "close paren":
            tokens.pop(0)
            return arguments
        arg = ast_assignment_expression(tokens)
        if arg is None:
            return None
        peekTok = ast_peek(tokens)
        if peekTok.type == "operator" and peekTok.contents == ",":
            tokens.pop(0)
        elif peekTok.type != "close paren":
            print("Function call arguments need a close paren")
            return None
        arguments.append(arg)


def ast_factor(tokens: list[token]) -> ast_nodes.Expression | None:
    nextTok = tokens.pop(0)
    if nextTok.type == "open paren":
        exp = ast_expression(tokens)
        if exp is None:
            return None
        c_paren = tokens.pop(0)
        if c_paren.type != "close paren":
            print("Factor must be closed by a parenthesis", c_paren)
            return None
        return exp
    elif nextTok.type == "operator" and nextTok.contents in ["-", "~", "!", "&", "*"]:
        operation = nextTok
        factor = ast_factor(tokens)
        if factor is None:
            return None
        return ast_operation(str(operation.contents), factor)
    elif nextTok.type == "operator" and nextTok.contents in ["++", "--"]:
        operation = nextTok
        identifier = ast_identifier(tok := tokens.pop(0))
        if identifier is None:
            print("Can only pre-increment identifiers.", f"Line: {tok.line}")
            return None
        return ast_nodes.Increment(identifier, True, operation.contents == "++")
    elif nextTok.type == "identifier":
        peekToken = ast_peek(tokens)
        if peekToken.contents in ["++", "--"]:
            operation = tokens.pop(0)
            # Post: i++ / i--
            identifier = ast_identifier(nextTok)
            if identifier is None:
                return None
            return ast_nodes.Increment(identifier, False, operation.contents == "++")
        if peekToken.type == "open paren":
            tokens.pop(0)
            arguments = ast_call_arguments(tokens)
            if arguments is None:
                return None
            var_id = ast_identifier(nextTok)
            if var_id is None:
                return None
            return ast_nodes.FunctionCall(var_id, arguments)
        if peekToken.type == "open bracket":
            tokens.pop(0)
            identifier = ast_identifier(nextTok)
            if identifier is None:
                return None
            access_index = ast_expression(tokens)
            if access_index is None:
                return None
            if (c_bracket := tokens.pop(0)).type != "close bracket":
                print(
                    "Syntax error: Expected closing bracket for array subscript.",
                    f"Line {c_bracket.line}",
                )
            return ast_nodes.arraySubscript(identifier, access_index)

        return ast_identifier(nextTok)
    elif nextTok.type == "literal integer" and type(nextTok.contents) is int:
        return ast_nodes.LiteralInteger(nextTok.contents)
    elif nextTok.type == "literal string" and type(nextTok.contents) is str:
        return ast_nodes.LiteralString(nextTok.contents)
    elif nextTok.type == "literal char" and type(nextTok.contents) is str:
        return ast_nodes.LiteralChar(nextTok.contents)
    elif nextTok.type == "keyword" and nextTok.contents in ["true", "false"]:
        return ast_nodes.LiteralBool(nextTok.contents == "true")
    else:
        if nextTok.type == "semicolon":
            print("Syntax error: Expected a value.", f"Line {nextTok.line}")
            return None
        print("Unknown factor token", nextTok)
        return None


def ast_term(tokens: list[token]) -> ast_nodes.Expression | None:
    factor = ast_factor(tokens)
    if factor is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["*", "/"]:
        operation = tokens.pop(0)
        nextFactor = ast_factor(tokens)
        if nextFactor is None or type(operation.contents) is not str:
            return None
        factor = ast_operation(operation.contents, factor, nextFactor)
        nextTok = ast_peek(tokens)
    return factor


def ast_additive_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_term(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["+", "-"]:
        operation = tokens.pop(0)
        nextTerm = ast_term(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitshift_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    factor = ast_additive_expression(tokens)
    if factor is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["<<", ">>"]:
        operation = tokens.pop(0)
        nextFactor = ast_additive_expression(tokens)
        if nextFactor is None or type(operation.contents) is not str:
            return None
        factor = ast_operation(operation.contents, factor, nextFactor)
        nextTok = ast_peek(tokens)
    return factor


def ast_relational_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_bitshift_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["<", ">", "<=", ">="]:
        operation = tokens.pop(0)
        nextTerm = ast_bitshift_expression(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_equality_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_relational_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["==", "!="]:
        operation = tokens.pop(0)
        nextTerm = ast_relational_expression(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitwise_and_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_equality_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "&":
        operation = tokens.pop(0)
        nextTerm = ast_equality_expression(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitwise_xor_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_bitwise_and_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "^":
        operation = tokens.pop(0)
        nextTerm = ast_bitwise_and_expression(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitwise_or_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_bitwise_xor_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "|":
        operation = tokens.pop(0)
        nextTerm = ast_bitwise_xor_expression(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_logical_and_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_bitwise_or_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "&&":
        operation = tokens.pop(0)
        nextTerm = ast_bitwise_or_expression(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_logical_or_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_logical_and_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "||":
        operation = tokens.pop(0)
        nextTerm = ast_logical_and_expression(tokens)
        if nextTerm is None or type(operation.contents) is not str:
            return None
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_conditional_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    term = ast_logical_or_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    if nextTok.type == "operator" and nextTok.contents == "?":
        tokens.pop(0)
        middle = ast_expression(tokens)
        if middle is None:
            return None
        colon = tokens.pop(0)
        if not (colon.type == "operator" and colon.contents == ":"):
            print("Conditional must have the colon '? <exp> : <exp>")
            return None
        end = ast_conditional_expression(tokens)
        if end is None:
            return None
        return ast_nodes.Conditional(term, middle, end)
    return term


def ast_assignment_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    is_assignment = len(tokens) >= 1 and ast_peek(tokens, 1).type == "assignment"
    tokens_copy = copy.deepcopy(tokens)
    tokens_copy.pop(0)
    subscript = tokens_copy.pop(0).type == "open bracket"
    if subscript:
        _ = ast_expression(tokens_copy)
        _ = tokens_copy.pop(0)  # close bracket
        is_assignment = (
            assigner := tokens_copy.pop(0)
        ).type == "assignment" or is_assignment
        # print(b, c, d)
    # if len(tokens) >= 1 and ast_peek(tokens, 1).type in ["assignment", "open bracket"]:
    if is_assignment:
        v_name = ast_identifier(tok := tokens.pop(0))
        if v_name is None:
            print("Assignment left must be identifier", f"Line: {tok.line}")
            return None
        if subscript:
            _ = tokens.pop(0)
            sub_idx = ast_expression(tokens)
            close_bracket = tokens.pop(0).type == "close bracket"

            if not close_bracket:
                print("Syntax error: expected closing bracket after array subscript")
                return None
            if sub_idx is None:
                return None
            v_name = ast_nodes.arraySubscript(v_name, sub_idx)

        assigner = tokens.pop(0)

        v_expression = ast_assignment_expression(tokens)
        if v_expression is None:
            return None
        if assigner.contents == "=":
            return ast_nodes.Assignment(v_name, v_expression)
        elif assigner.contents in [
            "+=",
            "-=",
            "*=",
            "<<=",
            ">>=",
            "&=",
            "^=",
            "|=",
        ]:
            return ast_nodes.Assignment(
                v_name,
                ast_operation(
                    assigner.contents[:-1],
                    v_name,
                    v_expression,
                ),
            )
        else:
            print(f"Unknown assigner: {assigner.contents}", f"Line: {assigner.line}")
    else:
        term = ast_conditional_expression(tokens)
        if term is None:
            return None
        return term


def ast_expression(tokens: list[token]) -> ast_nodes.Expression | None:
    if ast_peek(tokens).type == "semicolon":
        return ast_nodes._none()
    term = ast_assignment_expression(tokens)
    if term is None:
        return None
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == ",":
        tokens.pop(0)
        nextTerm = ast_assignment_expression(tokens)
        if nextTerm is None:
            return None
        term = ast_nodes.Comma(term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_declaration(tokens: list[token]) -> ast_nodes.Statement | None:
    tok = ast_peek(tokens)
    d_type = ast_type(tokens)
    if d_type is None:
        print("Syntax error: Declaration must have a type.", f"Line {tok.line}")
        return None
    d_name = ast_identifier(tok := tokens.pop(0))
    if d_name is None:
        print("Declaration type must be followed by identifier", tok)
        return None
    nextTok = tokens.pop(0)

    if nextTok.type == "open bracket":
        d_type = ast_nodes.Array(d_type)
        nextTok = tokens.pop(0)
        if nextTok.type != "close bracket":
            if nextTok.type != "literal integer":
                print("Array length must be literal Integer")
                return None
            print("Array length", nextTok)
            d_type.length = int(nextTok.contents)
            nextTok = tokens.pop(0)

        if nextTok.type != "close bracket":
            print("Syntax error: expected closing bracket after array length", nextTok)
            return None
        nextTok = tokens.pop(0)

    if nextTok.type == "assignment" and nextTok.contents == "=":
        d_value = ast_expression(tokens)
        if d_value is None:
            return None
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print("Declaration must end with a semicolon", semicolon)
            return None
        return ast_nodes.DeclarationAssignment(d_type, d_name, d_value)
    if nextTok.type != "semicolon":
        print(
            "Syntax error: Declaration must be followed by semicolon or assignment.",
            f"Line {nextTok.line}",
        )
        return None
    return ast_nodes.Declaration(d_type, d_name)


def ast_statement(tokens: list[token]) -> ast_nodes.Statement | None:
    token = ast_peek(tokens)
    if token.type == "type":  # declaration
        return ast_declaration(tokens)
    elif token.type == "keyword" and token.contents == "return":
        tokens.pop(0)
        r_value = ast_expression(tokens)
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print(
                "Syntax error: Statement must end with semicolon.",
                f"Line {semicolon.line}",
            )
            return None
        return ast_nodes.Return(r_value)
    elif token.type == "keyword" and token.contents == "if":
        tokens.pop(0)
        o_paren = tokens.pop(0)
        if o_paren.type != "open paren":
            print(
                "Syntax error: 'if' must be followed by open paren.",
                f"Line {o_paren.line}",
            )
            return None
        conditional = ast_expression(tokens)
        if conditional is None:
            return None
        c_paren = tokens.pop(0)
        if c_paren.type != "close paren":
            print(
                "Syntax error: 'if' conditional, unmatched paren.",
                f"Line {c_paren.line}",
            )
            return None
        statement = ast_statement(tokens)
        if statement is None:
            return None
        if type(if_state := statement) is ast_nodes.If:
            nest_cond = if_state.condition
            conditional = ast_operation("&&", conditional, nest_cond)
            statement = if_state.statement
        if (
            type(block := statement) is ast_nodes.Block
            and len(block.statements) == 1
            and type(block.statements[0]) is ast_nodes.If
        ):
            nest_cond = block.statements[0].condition
            conditional = ast_operation("&&", conditional, nest_cond)
            statement = block.statements[0].statement
        maybe_else = ast_peek(tokens)
        if maybe_else.type == "keyword" and maybe_else.contents == "else":
            tokens.pop(0)
            elseStatement = ast_statement(tokens)
            if elseStatement is None:
                return None
            return ast_nodes.IfElse(conditional, statement, elseStatement)
        return ast_nodes.If(conditional, statement)
    elif token.type == "open brace":
        tokens.pop(0)
        f_statements = ast_statement_collection(tokens)
        if f_statements is None:
            return None
        return ast_nodes.Block(f_statements)
    elif token.type == "keyword" and token.contents == "while":
        tokens.pop(0)
        o_paren = tokens.pop(0)
        if o_paren.type != "open paren":
            print(
                "Syntax error: 'while' must be followed by open paren.",
                f"Line {o_paren.line}",
            )
            return None
        conditional = ast_expression(tokens)
        if conditional is None:
            return None
        c_paren = tokens.pop(0)
        if c_paren.type != "close paren":
            print(
                "Syntax error: 'while' conditional, unmatched paren.",
                f"Line {c_paren.line}",
            )
            return None
        statement = ast_statement(tokens)
        if statement is None:
            return None
        return ast_nodes.While(conditional, statement)
    elif token.type == "keyword" and token.contents == "do":
        tokens.pop(0)
        statement = ast_statement(tokens)
        if statement is None:
            return None
        need_while = tokens.pop(0)
        if need_while.type != "keyword" or need_while.contents != "while":
            print("Syntax error: 'do' requires a 'while'.", f"Line: {need_while.line}")
            return None
        o_paren = tokens.pop(0)
        if o_paren.type != "open paren":
            print(
                "Syntax error: 'while' must be followed by open paren.",
                f"Line {o_paren.line}",
            )
            return None
        conditional = ast_expression(tokens)
        if conditional is None:
            return None
        c_paren = tokens.pop(0)
        if c_paren.type != "close paren":
            print(
                "Syntax error: 'while' conditional, unmatched paren.",
                f"Line {c_paren.line}",
            )
            return None
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print(
                "Syntax error: Statement must end with semicolon.",
                f"Line {semicolon.line}",
            )
            return None
        return ast_nodes.DoWhile(conditional, statement)
    elif token.type == "keyword" and token.contents == "for":
        tokens.pop(0)
        o_paren = tokens.pop(0)
        if o_paren.type != "open paren":
            print(
                "Syntax error: 'for' must be followed by open paren.",
                f"Line {o_paren.line}",
            )
            return None
        if ast_peek(tokens).type == "type":  # declaration
            initialExpression = ast_declaration(tokens)
            if initialExpression is None:
                return None
        else:
            initialExpression = ast_expression(tokens)
            if initialExpression is None:
                return None
            semicolon = tokens.pop(0)
            if semicolon.type != "semicolon":
                print(
                    "Syntax error: Missing semicolon.",
                    f"Line {semicolon.line}",
                )
                return None
        conditional = ast_expression(tokens)
        if conditional is None:
            return None
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print(
                "Syntax error: Missing semicolon.",
                f"Line {semicolon.line}",
            )
            return None
        postExpression = ast_expression(tokens)
        if postExpression is None:
            return None
        c_paren = tokens.pop(0)
        if c_paren.type != "close paren":
            print(
                "Syntax error: 'for' conditional, unmatched paren.",
                f"Line {c_paren.line}",
            )
            return None
        statement = ast_statement(tokens)
        if statement is None:
            return None
        return ast_nodes.ForLoop(
            initialExpression, conditional, postExpression, statement
        )
    elif token.type == "keyword" and token.contents == "continue":
        tokens.pop(0)
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print(
                "Syntax error: Missing semicolon.",
                f"Line {semicolon.line}",
            )
            return None
        return ast_nodes.Continue()
    elif token.type == "keyword" and token.contents == "break":
        tokens.pop(0)
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print(
                "Syntax error: Missing semicolon.",
                f"Line {semicolon.line}",
            )
            return None
        return ast_nodes.Break()
    elif token.type == "keyword" and token.contents == "asm":
        tokens.pop(0)
        tok = tokens.pop(0)
        if tok.type != "open brace":
            print("Syntax error: expected '{' after 'asm', got", tok)
            return None
        startLine = tok.line
        asmLines = []
        uid = str(uuid.uuid4())[:8]
        while (tok := tokens.pop(0)).type != "close brace":
            thisLine = tok.line - startLine
            while thisLine > len(asmLines) - 1:
                asmLines.append("")
            if tok.contents == "%":
                asmLines[thisLine] += uid + "_"
            elif tok.contents == ":":
                if asmLines[thisLine].endswith(" "):
                    asmLines[thisLine] = asmLines[thisLine][:-1]
                asmLines[thisLine] += str(tok.contents) + " "
            else:
                asmLines[thisLine] += str(tok.contents) + " "

        asmLines = [x.strip() for x in asmLines]
        asmLines.append("")
        asmLines.append("")
        # tokens.pop(0)
        # print(asmLines)
        # print(tokens)

        return ast_nodes.LiteralASM(asmLines)
    else:
        tryExpression = ast_expression(tokens)
        if tryExpression is None:
            return None
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print(
                "Syntax error: Statement must end with semicolon.",
                f"Line {semicolon.line}",
            )
            return None
        return tryExpression


def ast_statement_collection(tokens: list[token]) -> list | None:
    statementList = []
    trimming = False
    mentionedTrimming = False
    while True:
        peekToken = ast_peek(tokens)
        if peekToken.type == "close brace":
            tokens.pop(0)
            return statementList
        statement = ast_statement(tokens)
        if statement is None:
            return None
        if not trimming:
            statementList.append(statement)
            if type(statement) is ast_nodes.Return:
                trimming = True
        elif not mentionedTrimming:
            print("Trimming unreachable code after return.", f"Line: {peekToken.line}")
            mentionedTrimming = True


def ast_directive(tokens: list[token]) -> ast_nodes.Node | None:
    directive = tokens.pop(0)
    if directive.contents == "include":
        fileName = tokens.pop(0)
        if fileName.type != "literal string":
            print("Expected string path to include")
            return None
        return ast_nodes.Include(fileName.contents)
    else:
        print("Unknown directive:", directive)
        return None


def ast_toplevel(tokens: list[token]) -> ast_nodes.Node | None:
    tok = ast_peek(tokens)

    if tok.type == "symbol" and tok.contents == "#":
        tokens.pop(0)
        return ast_directive(tokens)

    _type = ast_type(tokens)
    if _type is None:
        print("Declaration must start with a type", tok)
        return None
    _name = ast_identifier(tok := tokens.pop(0))
    if _name is None:
        print("Declaration type must be followed by identifier", tok)
        return None
    peekTok = ast_peek(tokens)
    if peekTok.type == "semicolon":
        _ = tokens.pop(0)
        return ast_nodes.Declaration(_type, _name)
    elif peekTok.type == "assignment" and peekTok.contents == "=":
        _ = tokens.pop(0)
        _expr = ast_expression(tokens)
        if _expr is None:
            return None
        semicolon = tokens.pop(0)
        if semicolon.type != "semicolon":
            print("Declaration must end with a semicolon", semicolon)
            return None
        return ast_nodes.DeclarationAssignment(_type, _name, _expr)

    # first_type = ast_peek(tokens, 1)
    # if first_type.type == "type" and first_type.contents == "void":
    #     f_arguments = []
    #     oparen = tokens.pop()
    #     cparent = tokens.pop()
    # else:
    f_arguments = ast_arguments(tokens)

    if f_arguments is None:
        return None

    # print(list(arg._type.type is ast_nodes.basetypes._void for arg in f_arguments))
    # if any(arg._type.type is ast_nodes.basetypes._void for arg in f_arguments):
    #     print("VOID")

    token = tokens.pop(0)
    if token.type == "semicolon":
        return ast_nodes.FunctionPrototype(_type, _name, f_arguments)
    elif token.type != "open brace":
        print("Statement must start with open brace", token)
        return None
    f_statements = ast_statement_collection(tokens)
    if f_statements is None:
        return None
    return ast_nodes.Function(_type, _name, f_arguments, f_statements)


def ast_head(tokens: list[token]) -> list[ast_nodes.Node]:
    head = []
    while len(tokens) > 0:
        f = ast_toplevel(tokens)
        if f is None:
            return []
        else:
            head.append(f)
    return head


if __name__ == "__main__":
    from tokenizer import tokenize, token

    file = Path("test.g")
    with open(file, "r") as f:
        fileContents: str = f.read()

    tokens: list[token] = tokenize(fileContents, file)

    # print(tokens)
    AST: list[ast_nodes.Node] = ast_head(tokens)
    if AST == []:
        print("SAD (No AST output...)")
        exit()
    print(AST)
