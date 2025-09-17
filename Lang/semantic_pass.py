from enum import StrEnum
from io import StringIO
from os import symlink
import ast_nodes
from ast_nodes import Type

scope = []


class Symbol:
    _type = "Symbol"
    created_in_current_context: bool = True
    name: str
    was_read: bool = False
    was_set: bool = False
    value: str

    def __init__(self, name: str):
        self.name = name

    def prettyOut(self):
        print(self._type, self.name)


import semantic_errors


class FunctionSymbol(Symbol):
    _type = "Function"
    origin_node: ast_nodes.Function


class DeclarationSymbol(Symbol):
    _type = "Declaration"
    origin_node: ast_nodes.Declaration


class ScopeStack:
    scopeList: list[list[Symbol]]

    def __init__(self):
        self.scopeList = [[]]

    def add(self, symbol: Symbol) -> bool:  # Returns Success
        if self.find(symbol.name):
            return False
        self.scopeList[-1].append(symbol)
        return True

    def prettyOut(self) -> None:
        print("Scope Stack:")
        for symbolList in self.scopeList:
            print("===")
            for sym in symbolList:
                sym.prettyOut()

    def push(self) -> None:
        self.scopeList.append([])

    def pop(self) -> None:
        if len(self.scopeList) < 2:
            print("Internal Error: You can't pop the global scope, silly")
            exit(1)
        self.scopeList.pop(0)

    def find(self, name: str) -> Symbol | None:
        for symbolList in self.scopeList:
            for symbol in symbolList:
                if symbol.name == name:
                    return symbol

    def cur_scope(self, name: str) -> bool:
        return name in [symbol.name for symbol in self.scopeList[-1]]


def semantic_function(node: ast_nodes.Function, scope: ScopeStack):
    func_sym = FunctionSymbol(node.id.name)
    scope.add(func_sym)
    func_sym.origin_node = node


def semantic_declaration(node: ast_nodes.Declaration, scope: ScopeStack):
    decl_sym = DeclarationSymbol(node.id.name)
    scope.add(decl_sym)
    decl_sym.origin_node = node


# def semantic_statement(node: ast_nodes.Statement):
#     pass


def semantic_head(nodes: list[ast_nodes.Statement]):
    globalScope = ScopeStack()
    for node in nodes:
        # print(i, type(i))
        # if type(mainNode) is ast_nodes.FunctionPrototype:
        # elif type(mainNode) is ast_nodes.DeclarationAssignment:
        if isinstance(node, ast_nodes.Function):
            semantic_function(node, globalScope)
        elif isinstance(node, ast_nodes.Declaration):
            semantic_declaration(node, globalScope)
        else:
            print("Unknown node", node, type(node))
            exit(1)
    globalScope.prettyOut()
    return nodes


if __name__ == "__main__":
    from tokenizer import tokenize, Token
    from my_ast import ast_head
    from pathlib import Path

    file = "test.g"
    with open(file, "r") as f:
        fileContents: str = f.read()

    tokens: list[Token] = tokenize(fileContents, Path(file))

    # print(tokens)
    AST: list[ast_nodes.Node] = ast_head(tokens)
    if AST == []:
        exit()
    AST = semantic_head(AST)
