#!/usr/bin/env python3

from tokenizer import tokenize, Token
from construct import construct
from my_ast import ast_head
from semantic_pass import semantic_head
from ast_nodes import Node
import sys
from pathlib import Path


def compile(fileName: Path, fs=False) -> str:
    with open(fileName, "r") as f:
        fileContents: str = f.read()

    tokens: list[Token] = tokenize(fileContents, fileName)
    # print(tokens)

    AST: list[Node] = ast_head(tokens)
    # if AST == []:
    #     print("SAD (No AST output...)")
    #     exit(1)
    # print(AST)

    AST = semantic_head(AST)

    assembly = str(construct(AST, fs))
    # print(assembly)
    return assembly


def main():
    args = sys.argv[1:]
    fs = False
    if len(args) == 0:
        file = Path("test.g")
    else:
        file = Path(args[0])
        if not file.exists():
            print("Failed to load file", args[0])
            exit(1)
        if len(args) > 1 and args[1] == "-fs":
            fs = True

    assembly = compile(file, fs=fs)
    outfile = str(file.resolve()).rsplit(".", 1)[0] + ".ghasm"
    with open(outfile, "w+") as f:
        f.write(assembly)
    print(f"Writing to {outfile.split('/')[-1]}")


if __name__ == "__main__":
    main()
