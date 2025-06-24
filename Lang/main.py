#!/usr/bin/env python3

from tokenizer import tokenize, token
from construct import construct
from my_ast import ast_head
from ast_nodes import Node
import sys
from pathlib import Path


if __name__ != "__main__":
    exit()


args = sys.argv[1:]
if len(args) == 0:
    file = Path("test.g")
    # print("Must give a file to build")
else:
    file = Path(args[0])

with open(file, "r") as f:
    fileContents: str = f.read()


tokens: list[token] = tokenize(fileContents, file)

# print(tokens)

AST: list[Node] = ast_head(tokens)
if AST == []:
    print("SAD (No AST output...)")
    exit()
# print(AST)
assembly = str(construct(AST))
# print(assembly)
outfile = ".".join(str(file.resolve()).split(".")[:-1]) + ".ghasm"
with open(outfile, "w+") as f:
    f.write(assembly)
print(f"Writing to {outfile.split('/')[-1]}")
