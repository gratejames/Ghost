from tokenizer import Token
import ast_nodes
import ast_errors
from pathlib import Path
import uuid
import copy


def ast_type(tokens: list[Token]) -> ast_nodes.Type:
    _type = ast_pop(tokens)
    if _type.type != "type" or type(_type.contents) is not str:
        raise ast_errors.Expected(_type, "type")

    t = ast_nodes.Type(_type.contents)

    nextTok = ast_peek(tokens)
    if nextTok.type == "operator" and nextTok.contents == "*":
        ast_pop(tokens)
        return ast_nodes.Pointer(t)

    return t


def ast_typeNode(tokens: list[Token]) -> ast_nodes.TypeNode:
    _type = ast_pop(tokens)
    if _type.type != "type" or type(_type.contents) is not str:
        raise ast_errors.Expected(_type, "type")

    t = ast_nodes.TypeNode(ast_nodes.Type(_type.contents), _type)

    nextTok = ast_peek(tokens)
    if nextTok.type == "operator" and nextTok.contents == "*":
        ast_pop(tokens)
        t.type = ast_nodes.Pointer(t.type)
        return t

    return t


def ast_identifier(_id: Token) -> ast_nodes.Identifier:
    if (
        _id.type != "identifier"
        or type(_id.contents) is not str
        or len(_id.contents) == 0
    ):
        raise ast_errors.Expected(_id, "identifier")
    if not _id.contents[0].isalpha():
        raise ast_errors.SyntaxError(_id, "Identifier must start with a letter")
    return ast_nodes.Identifier(_id.contents, _id)


def ast_peek(tokens: list[Token], i: int = 0) -> Token:
    if len(tokens) > i:
        return tokens[i]
    raise ast_errors.SyntaxError(None, "Unexpected EOF")


def ast_pop(tokens: list[Token]):
    if len(tokens) > 0:
        return tokens.pop(0)
    raise ast_errors.SyntaxError(None, "Unexpected EOF")


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
        # if isinstance(operand_a, ast_nodes.LiteralInteger):
        #     match operation_type:
        #         case "-":
        #             return ast_nodes.LiteralInteger(-operand_a.value, operand_a.token)
        #         case "~":
        #             return ast_nodes.LiteralInteger(
        #                 op_invert(operand_a.value), operand_a.token
        #             )
        #         case "!":
        #             return ast_nodes.LiteralInteger(
        #                 int(operand_a.value == 0), operand_a.token
        #             )
        return ast_nodes.unOperation(operation_type, operand_a)
    else:
        # if isinstance(operand_a, ast_nodes.LiteralInteger) and operation_type in [
        #     "*",
        #     "+",
        # ]:
        #     temp = operand_a
        #     operand_a = operand_b
        #     operand_b = temp

        # if isinstance(operand_b, ast_nodes.LiteralInteger) and operation_type == "*":
        #     if operand_b.value == 0:
        #         return ast_nodes.LiteralInteger(0)
        #     if operand_b.value == 1:
        #         return operand_a

        # if isinstance(operand_b, ast_nodes.LiteralInteger) and operation_type in [
        #     "+",
        #     "-",
        #     "|",
        #     "^",
        # ]:
        #     if operand_b.value == 0:
        #         return operand_a

        # if isinstance(operand_b, ast_nodes.LiteralInteger) and operation_type == "&":
        #     if operand_b.value == 0xFFFF:
        #         return operand_a

        # if operation_type == "&&" and (
        #     (isinstance(operand_a, ast_nodes.LiteralInteger) and operand_a.value == 0)
        #     or (
        #         isinstance(operand_b, ast_nodes.LiteralInteger) and operand_b.value == 0
        #     )
        # ):
        #     return ast_nodes.LiteralInteger(0)

        # if operation_type == "||" and (
        #     (isinstance(operand_a, ast_nodes.LiteralInteger) and operand_a.value != 0)
        #     or (
        #         isinstance(operand_b, ast_nodes.LiteralInteger) and operand_b.value != 0
        #     )
        # ):
        #     return ast_nodes.LiteralInteger(1)

        # if isinstance(operand_a, ast_nodes.LiteralInteger) and isinstance(
        #     operand_b, ast_nodes.LiteralInteger
        # ):
        #     match operation_type:
        #         case "*":
        #             return ast_nodes.LiteralInteger(
        #                 operand_a.value * operand_b.value,
        #                 operand_a.token.combine(operand_b.token),
        #             )
        #         case "+":
        #             return ast_nodes.LiteralInteger(operand_a.value + operand_b.value)
        #         case "-":
        #             return ast_nodes.LiteralInteger(operand_a.value - operand_b.value)
        #         case "<<":
        #             return ast_nodes.LiteralInteger(operand_a.value << operand_b.value)
        #         case ">>":
        #             return ast_nodes.LiteralInteger(operand_a.value >> operand_b.value)
        #         case "&":
        #             return ast_nodes.LiteralInteger(operand_a.value & operand_b.value)
        #         case "|":
        #             return ast_nodes.LiteralInteger(operand_a.value | operand_b.value)
        #         case "^":
        #             return ast_nodes.LiteralInteger(operand_a.value ^ operand_b.value)

        return ast_nodes.biOperation(operation_type, operand_a, operand_b)


def ast_arguments(tokens: list[Token]) -> list[ast_nodes.FunctionArgument]:
    arguments: list[ast_nodes.FunctionArgument] = []
    o_paren = ast_pop(tokens)
    if o_paren.type != "open paren":
        # "Arguments must start with a paren"
        raise ast_errors.Expected(o_paren, "open parenthesis")
    while True:
        nextTok = ast_peek(tokens)
        if nextTok.type == "close paren":
            ast_pop(tokens)
            break

        a_type = ast_typeNode(tokens)
        if a_type.type.type is ast_nodes.basetypes._void:
            a_name = ast_nodes.Identifier("Void", a_type.token)
        else:
            a_name = ast_identifier(tok := ast_pop(tokens))
            # TODO Could try catch to provide a more contextualized error
            # if a_name is None: # UNREACHABLE WITHOUT TRY CATCH
            #     raise ast_errors.Expected(tok, "closing parenthesis")
            # Arguments type must be followed by identifier
        arguments.append(ast_nodes.FunctionArgument(a_type, a_name))

        peekTok = ast_peek(tokens)
        if peekTok.type == "operator" and peekTok.contents == ",":
            ast_pop(tokens)
            continue
        elif peekTok.type == "close paren":
            continue
        else:
            raise ast_errors.SyntaxError(peekTok, "Unknown argument token")

    if any(arg._type.type is ast_nodes.basetypes._void for arg in arguments):
        if len(arguments) != 1:
            raise ast_errors.SyntaxError(
                None, "If 'void' is the argument, it must stand alone."
            )
            # print("If 'void' is the argument, it must stand alone.")
            # # TODO needs blame. Methinks the only way to do this would be to have each expression (and maybe statement) keep track of it's tokens. Blegh
            # # [
            # #     arg.blame()
            # #     for arg in arguments
            # #     if arg._type.type is ast_nodes.basetypes._void
            # # ]
        else:
            arguments = []

    return arguments


def ast_call_arguments(
    tokens: list[Token],
) -> list[ast_nodes.Expression]:
    arguments: list[ast_nodes.Expression] = []
    while True:
        peekTok = ast_peek(tokens)
        if peekTok.type == "close paren":
            ast_pop(tokens)
            return arguments
        arg = ast_assignment_expression(tokens)
        peekTok = ast_peek(tokens)
        if peekTok.type == "operator" and peekTok.contents == ",":
            ast_pop(tokens)
        elif peekTok.type != "close paren":
            raise ast_errors.Expected(peekTok, "closing parenthesis")
        arguments.append(arg)


def ast_factor(tokens: list[Token]) -> ast_nodes.Expression:
    nextTok = ast_pop(tokens)
    if nextTok.type == "open paren":
        exp = ast_expression(tokens)
        c_paren = ast_pop(tokens)
        if c_paren.type != "close paren":
            raise ast_errors.Expected(c_paren, "closing parenthesis")
        return exp
    elif nextTok.type == "operator" and nextTok.contents in ["-", "~", "!", "&", "*"]:
        operation = nextTok
        factor = ast_factor(tokens)
        return ast_operation(str(operation.contents), factor)
    elif nextTok.type == "operator" and nextTok.contents in ["++", "--"]:
        operation = nextTok
        identifier = ast_identifier(tok := ast_pop(tokens))
        # if identifier is None: # UNREACHABLE WITHOUT TRY CATCH
        #     raise ast_errors.SyntaxError(tok, "Can only pre-increment identifiers.")
        return ast_nodes.Increment(identifier, True, operation.contents == "++")
    elif nextTok.type == "identifier":
        peekToken = ast_peek(tokens)
        if peekToken.contents in ["++", "--"]:
            operation = ast_pop(tokens)
            # Post: i++ / i--
            identifier = ast_identifier(nextTok)
            return ast_nodes.Increment(identifier, False, operation.contents == "++")
        if peekToken.type == "open paren":
            ast_pop(tokens)
            arguments = ast_call_arguments(tokens)
            var_id = ast_identifier(nextTok)
            return ast_nodes.FunctionCall(var_id, arguments)
        if peekToken.type == "open bracket":
            ast_pop(tokens)
            identifier = ast_identifier(nextTok)
            access_index = ast_expression(tokens)
            if (c_bracket := ast_pop(tokens)).type != "close bracket":
                raise ast_errors.Expected(c_bracket, "closing bracket")
                # "Syntax error: Expected closing bracket for array subscript."
            return ast_nodes.arraySubscript(identifier, access_index)

        return ast_identifier(nextTok)
    elif nextTok.type == "literal integer" and type(nextTok.value) is int:
        return ast_nodes.LiteralInteger(nextTok.value, nextTok)
    elif nextTok.type == "literal string" and type(nextTok.contents) is str:
        return ast_nodes.LiteralString(nextTok.contents, nextTok)
    elif nextTok.type == "literal char" and type(nextTok.contents) is str:
        return ast_nodes.LiteralChar(nextTok.contents, nextTok)
    elif nextTok.type == "keyword" and nextTok.contents in ["true", "false"]:
        return ast_nodes.LiteralBool(nextTok.contents == "true", nextTok)
    else:
        if nextTok.type == "semicolon":
            raise ast_errors.Expected(nextTok, "value")
            # "Syntax error: Expected a value."
        raise ast_errors.SyntaxError(nextTok, "Unknown factor token")


def ast_term(tokens: list[Token]) -> ast_nodes.Expression:
    factor = ast_factor(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["*", "/", "%"]:
        operation = ast_pop(tokens)
        nextFactor = ast_factor(tokens)
        factor = ast_operation(operation.contents, factor, nextFactor)
        nextTok = ast_peek(tokens)
    return factor


def ast_additive_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_term(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["+", "-"]:
        operation = ast_pop(tokens)
        nextTerm = ast_term(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitshift_expression(tokens: list[Token]) -> ast_nodes.Expression:
    factor = ast_additive_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["<<", ">>"]:
        operation = ast_pop(tokens)
        nextFactor = ast_additive_expression(tokens)
        factor = ast_operation(operation.contents, factor, nextFactor)
        nextTok = ast_peek(tokens)
    return factor


def ast_relational_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_bitshift_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["<", ">", "<=", ">="]:
        operation = ast_pop(tokens)
        nextTerm = ast_bitshift_expression(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_equality_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_relational_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents in ["==", "!="]:
        operation = ast_pop(tokens)
        nextTerm = ast_relational_expression(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitwise_and_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_equality_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "&":
        operation = ast_pop(tokens)
        nextTerm = ast_equality_expression(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitwise_xor_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_bitwise_and_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "^":
        operation = ast_pop(tokens)
        nextTerm = ast_bitwise_and_expression(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_bitwise_or_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_bitwise_xor_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "|":
        operation = ast_pop(tokens)
        nextTerm = ast_bitwise_xor_expression(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_logical_and_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_bitwise_or_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "&&":
        operation = ast_pop(tokens)
        nextTerm = ast_bitwise_or_expression(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_logical_or_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_logical_and_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == "||":
        operation = ast_pop(tokens)
        nextTerm = ast_logical_and_expression(tokens)
        term = ast_operation(operation.contents, term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_conditional_expression(tokens: list[Token]) -> ast_nodes.Expression:
    term = ast_logical_or_expression(tokens)
    nextTok = ast_peek(tokens)
    if nextTok.type == "operator" and nextTok.contents == "?":
        ast_pop(tokens)
        middle = ast_expression(tokens)
        colon = ast_pop(tokens)
        if not (colon.type == "operator" and colon.contents == ":"):
            raise ast_errors.Expected(colon, "colon")
            # expected colon in conditional
        end = ast_conditional_expression(tokens)
        return ast_nodes.Conditional(term, middle, end)
    return term


def ast_assignment_expression(tokens: list[Token]) -> ast_nodes.Expression:
    is_assignment = len(tokens) >= 1 and ast_peek(tokens, 1).type == "assignment"
    tokens_copy = copy.deepcopy(tokens)
    ast_pop(tokens_copy)
    subscript = ast_pop(tokens_copy).type == "open bracket"
    if subscript:
        _ = ast_expression(tokens_copy)
        _ = ast_pop(tokens_copy)  # close bracket
        is_assignment = (
            assigner := ast_pop(tokens_copy)
        ).type == "assignment" or is_assignment
        # print(b, c, d)
    # if len(tokens) >= 1 and ast_peek(tokens, 1).type in ["assignment", "open bracket"]:
    if is_assignment:
        v_name = ast_identifier(tok := ast_pop(tokens))
        # if v_name is None: # UNREACHABLE WITHOUT TRY CATCH
        #     raise ast_errors.Expected(tok, "assignment")
        # Syntax error: Assignment left must be identifier
        if subscript:
            _ = ast_pop(tokens)
            sub_idx = ast_expression(tokens)
            close_bracket = ast_pop(tokens)

            if not close_bracket.type == "close bracket":
                raise ast_errors.Expected(close_bracket, "closing bracket")
                # expected closing bracket after array subscript
            v_name = ast_nodes.arraySubscript(v_name, sub_idx)

        assigner = ast_pop(tokens)

        v_expression = ast_assignment_expression(tokens)
        if assigner.contents == "=":
            return ast_nodes.Assignment(v_name, v_expression)
        elif assigner.contents in [
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
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
            raise ast_errors.SyntaxError(assigner, "unknown assigner")
    else:
        term = ast_conditional_expression(tokens)
        return term


def ast_expression(tokens: list[Token]) -> ast_nodes.Expression:
    # if ast_peek(tokens).type == "semicolon":
    #     return ast_nodes._none()
    # TODO: A none expression makes no sense. A 'statement' does, but not an expression
    # Maybe this was meant to help empty for loops? Not sure
    term = ast_assignment_expression(tokens)
    nextTok = ast_peek(tokens)
    while nextTok.type == "operator" and nextTok.contents == ",":
        ast_pop(tokens)
        nextTerm = ast_assignment_expression(tokens)
        term = ast_nodes.Comma(term, nextTerm)
        nextTok = ast_peek(tokens)
    return term


def ast_declaration(tokens: list[Token]) -> ast_nodes.Statement:
    tok = ast_peek(tokens)
    d_type = ast_typeNode(tokens)
    # if d_type is None: # UNREACHABLE WITHOUT TRY CATCH
    #     raise ast_errors.Expected(tok, "type")
    # Declaration must have a type.
    d_name = ast_identifier(tok := ast_pop(tokens))
    # if d_name is None: # UNREACHABLE WITHOUT TRY CATCH
    #     raise ast_errors.Expected(tok, "Declaration")
    # Declaration type must be followed by identifier
    nextTok = ast_pop(tokens)

    # if nextTok.type == "open bracket":
    #     d_array = ast_nodes.LiteralArray(d_type)
    #     nextTok = ast_pop(tokens)
    #     if nextTok.type != "close bracket":
    #         if nextTok.type != "literal integer":
    #             raise ast_errors.Expected(nextTok, "literal integer")
    #             # Array length must be literal Integer
    #         print("Array length", nextTok)
    #         d_array.length = nextTok.value
    #         nextTok = ast_pop(tokens)

    #     if nextTok.type != "close bracket":
    #         raise ast_errors.Expected(nextTok, "closing bracket")
    #         # Syntax error: expected closing bracket after array length
    #     nextTok = ast_pop(tokens)

    if nextTok.type == "assignment" and nextTok.contents == "=":
        d_value = ast_expression(tokens)
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Declaration must end with a semicolon
        return ast_nodes.DeclarationAssignment(d_type, d_name, d_value)
    if nextTok.type != "semicolon":
        raise ast_errors.Expected(nextTok, "semicolon")
        # Declaration must be followed by semicolon or assignment.
    return ast_nodes.Declaration(d_type, d_name)


def ast_statement(tokens: list[Token]) -> ast_nodes.Statement:
    token = ast_peek(tokens)
    if token.type == "type":  # declaration
        return ast_declaration(tokens)
    elif token.type == "keyword" and token.contents == "return":
        ast_pop(tokens)
        r_value = ast_expression(tokens)
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Syntax error: Statement must end with semicolon.
        return ast_nodes.Return(r_value, token)
    elif token.type == "keyword" and token.contents == "if":
        ast_pop(tokens)
        o_paren = ast_pop(tokens)
        if o_paren.type != "open paren":
            raise ast_errors.Expected(o_paren, "open parenthesis")
            # 'if' must be followed by open paren.
        conditional = ast_expression(tokens)
        c_paren = ast_pop(tokens)
        if c_paren.type != "close paren":
            raise ast_errors.Expected(c_paren, "closing parenthesis")
            # 'if' conditional, unmatched paren.
        statement = ast_statement(tokens)
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
            ast_pop(tokens)
            elseStatement = ast_statement(tokens)
            return ast_nodes.IfElse(conditional, statement, elseStatement)
        return ast_nodes.If(conditional, statement)
    elif token.type == "open brace":
        ast_pop(tokens)
        f_statements = ast_statement_collection(tokens)
        return ast_nodes.Block(f_statements)
    elif token.type == "keyword" and token.contents == "while":
        ast_pop(tokens)
        o_paren = ast_pop(tokens)
        if o_paren.type != "open paren":
            raise ast_errors.Expected(o_paren, "open parenthesis")
            # 'while' must be followed by open paren.
        conditional = ast_expression(tokens)
        c_paren = ast_pop(tokens)
        if c_paren.type != "close paren":
            raise ast_errors.Expected(c_paren, "closing parenthesis")
            # 'while' conditional, unmatched paren.
        statement = ast_statement(tokens)
        return ast_nodes.While(conditional, statement)
    elif token.type == "keyword" and token.contents == "do":
        ast_pop(tokens)
        statement = ast_statement(tokens)
        need_while = ast_pop(tokens)
        if need_while.type != "keyword" or need_while.contents != "while":
            raise ast_errors.Expected(need_while, "while")
            # 'do' requires a 'while'.
        o_paren = ast_pop(tokens)
        if o_paren.type != "open paren":
            raise ast_errors.Expected(o_paren, "open parenthesis")
            # 'while' must be followed by open paren.
        conditional = ast_expression(tokens)
        c_paren = ast_pop(tokens)
        if c_paren.type != "close paren":
            raise ast_errors.Expected(c_paren, "closing parenthesis")
            # 'while' conditional, unmatched paren.
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Statement must end with semicolon.
        return ast_nodes.DoWhile(conditional, statement)
    elif token.type == "keyword" and token.contents == "for":
        print(tokens)
        ast_pop(tokens)
        o_paren = ast_pop(tokens)
        if o_paren.type != "open paren":
            raise ast_errors.Expected(o_paren, "open parenthesis")
            # 'for' must be followed by open paren.
        if ast_peek(tokens).type == "type":  # declaration
            initialExpression = ast_declaration(tokens)
        else:
            if ast_peek(tokens).type == "semicolon":
                initialExpression = ast_nodes._none()
                _ = ast_pop(tokens)
            else:
                initialExpression = ast_expression(tokens)
                semicolon = ast_pop(tokens)
                if semicolon.type != "semicolon":
                    raise ast_errors.Expected(semicolon, "semicolon")
                    # Missing semicolon in for-pre.
        if ast_peek(tokens).type == "semicolon":
            conditional = ast_nodes._none()
        else:
            conditional = ast_expression(tokens)
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Missing semicolon in for-condition.
        if ast_peek(tokens).type == "close paren":
            postExpression = ast_nodes._none()
        else:
            postExpression = ast_expression(tokens)
        c_paren = ast_pop(tokens)
        if c_paren.type != "close paren":
            raise ast_errors.Expected(c_paren, "closing parenthesis")
            #'for' conditional, unmatched paren.
        statement = ast_statement(tokens)
        return ast_nodes.ForLoop(
            initialExpression, conditional, postExpression, statement
        )
    elif token.type == "keyword" and token.contents == "continue":
        ast_pop(tokens)
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Missing semicolon.
        return ast_nodes.Continue(token)
    elif token.type == "keyword" and token.contents == "break":
        ast_pop(tokens)
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Missing semicolon.
        return ast_nodes.Break(token)
    elif token.type == "keyword" and token.contents == "asm":
        ast_pop(tokens)
        tok = ast_pop(tokens)
        if tok.type != "open brace":
            raise ast_errors.Expected(tok, "open brace")
            # expected '{' after 'asm'
        startLine = tok.line
        asmLines = []
        uid = str(uuid.uuid4())[:8]
        while (tok := ast_pop(tokens)).type != "close brace":
            thisLine = tok.line - startLine
            while thisLine > len(asmLines) - 1:
                asmLines.append("")
            if tok.contents == "%":
                asmLines[thisLine] += uid + "_"
            elif tok.contents == ":":
                if asmLines[thisLine].endswith(" "):
                    asmLines[thisLine] = asmLines[thisLine][:-1]
                asmLines[thisLine] += str(tok.contents) + " "
            elif tok.contents == "$":
                asmLines[thisLine] += str(tok.contents)
            else:
                asmLines[thisLine] += str(tok.contents) + " "

        asmLines = [x.strip() for x in asmLines]
        asmLines.append("")
        asmLines.append("")
        # ast_pop(tokens)
        # print(asmLines)
        # print(tokens)

        return ast_nodes.LiteralASM(asmLines)
    elif token.type == "semicolon":
        ast_pop(tokens)
        return ast_nodes._none()
    else:
        tryExpression = ast_expression(tokens)
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Statement must end with semicolon.
        return tryExpression


def ast_statement_collection(tokens: list[Token]) -> list:
    statementList = []
    trimming = False
    mentionedTrimming = False
    while True:
        peekToken = ast_peek(tokens)
        if peekToken.type == "close brace":
            ast_pop(tokens)
            return statementList
        statement = ast_statement(tokens)
        if not trimming:
            statementList.append(statement)
            if type(statement) is ast_nodes.Return:
                trimming = True
        elif not mentionedTrimming:
            print(
                "Warning: Trimming unreachable code after return.",
                f"Line: {peekToken.line}",
            )
            mentionedTrimming = True


def ast_directive(tokens: list[Token]) -> ast_nodes.Node:
    directive = ast_pop(tokens)
    if directive.contents == "include":
        fileName = ast_pop(tokens)
        if fileName.type != "literal string":
            raise ast_errors.Expected(fileName, "string path")
            # Syntax error: Expected string path to include
        return ast_nodes.Include(fileName.contents)
    else:
        raise ast_errors.SyntaxError(directive, "Unknown directive")
        # Unknown directive


def ast_toplevel(tokens: list[Token]) -> ast_nodes.Node:
    tok = ast_peek(tokens)

    if tok.type == "symbol" and tok.contents == "#":
        ast_pop(tokens)
        return ast_directive(tokens)

    _type = ast_typeNode(tokens)
    # if _type is None: # UNREACHABLE WITHOUT TRY CATCH
    #     raise ast_errors.Expected(tok, "type")
    # Declaration must start with a type
    _name = ast_identifier(tok := ast_pop(tokens))
    # if _name is None:  # UNREACHABLE WITHOUT TRY CATCH
    #     raise ast_errors.Expected(tok, "identifier")
    # Declaration type must be followed by identifier
    peekTok = ast_peek(tokens)
    if peekTok.type == "semicolon":
        _ = ast_pop(tokens)
        return ast_nodes.Declaration(_type, _name)
    elif peekTok.type == "assignment" and peekTok.contents == "=":
        _ = ast_pop(tokens)
        _expr = ast_expression(tokens)
        semicolon = ast_pop(tokens)
        if semicolon.type != "semicolon":
            raise ast_errors.Expected(semicolon, "semicolon")
            # Syntax error: Declaration must end with a semicolon
        return ast_nodes.DeclarationAssignment(_type, _name, _expr)

    # first_type = ast_peek(tokens, 1)
    # if first_type.type == "type" and first_type.contents == "void":
    #     f_arguments = []
    #     oparen = tokens.pop()
    #     cparent = tokens.pop()
    # else:
    f_arguments = ast_arguments(tokens)

    # print(list(arg._type.type is ast_nodes.basetypes._void for arg in f_arguments))
    # if any(arg._type.type is ast_nodes.basetypes._void for arg in f_arguments):
    #     print("VOID")

    token = ast_pop(tokens)
    if token.type == "semicolon":
        return ast_nodes.FunctionPrototype(_type, _name, f_arguments)
    elif token.type != "open brace":
        raise ast_errors.Expected(tok, "open brace")
        # Statement must start with open brace
    f_statements = ast_statement_collection(tokens)
    return ast_nodes.Function(_type, _name, f_arguments, f_statements)


def ast_head(tokens: list[Token]) -> list[ast_nodes.Node]:
    head = []
    while len(tokens) > 0:
        f = ast_toplevel(tokens)
        head.append(f)
    return head


if __name__ == "__main__":
    from tokenizer import tokenize, Token

    file = Path("test.g")
    with open(file, "r") as f:
        fileContents: str = f.read()

    tokens: list[Token] = tokenize(fileContents, file)

    AST: list[ast_nodes.Node] = ast_head(tokens)
    if AST == []:
        print("SAD (No AST output...)")
        exit()
    print(AST)

    # def recurseBlame(node: ast_nodes.Node):
    #     if type(node) is ast_nodes.Function:
    #         node.typenode.blame()
    #         node.id.blame()
    #         for arg in node.args:
    #             recurseBlame(arg)
    #         for statement in node.statements:
    #             recurseBlame(statement)
    #     elif type(node) is ast_nodes.DeclarationAssignment:
    #         node.typenode.blame()
    #         node.id.blame()
    #         node.expr.blame()
    #     elif type(node) is ast_nodes.Declaration:
    #         node.typenode.blame()
    #         node.id.blame()
    #     elif type(node) is ast_nodes.FunctionCall:
    #         node.id.blame()
    #         for arg in node.args:
    #             arg.blame()
    #     elif type(node) is ast_nodes.FunctionArgument:
    #         node.blame()
    #         node.typenode.blame()
    #     else:
    #         node.blame()

    # # Blame Debugging
    # for node in AST:
    #     recurseBlame(node)
