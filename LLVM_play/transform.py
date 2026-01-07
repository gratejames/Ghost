# import nodes
import parser

from flatten import flatten
from lifetimes import lifetimes
from printer import printer

p = parser.parser("prime.ll")
for f in p.parsedFuncs:
    p.parseFunction(f)

# print(p.parsedFuncs[0].blocks[2].registers)
# print(p.parsedFuncs[0].blocks[2].memoryeffects)
# exit()

arr = flatten(p.functions)

# l = lifetimes(arr)
# l.process()
# lifetimes = l.textout()
# l.resolve()
# resolved = l.textout()


# # def stringify(node):
# #     nodetext = str(node)
# #     return "    " * node.indent + nodetext


# # strarr = [stringify(line) for line in arr]
# # mlen = max(len(line) for line in strarr)


# # def pad(line, length):
# #     line += " " * (length - len(line))
# #     return line


# # print("\n".join(pad(line, mlen) for i, line in enumerate(strarr)))
# # print("\n".join(pad(line, mlen) + "  " + resolved[i] for i, line in enumerate(strarr)))
# # print(
# #     "\n".join(
# #         pad(line, mlen) + " " * padding + lifetimes[i] + " " * padding + resolved[i]
# #         for i, line in enumerate(strarr)
# #     )
# # )
# #
# # print(l.translations)


# prnt = printer(arr, l.translations, p.globals)

# ASM = prnt.out()
# # print(ASM)
# with open("out.ghasm", "w+") as f:
#     f.write(ASM)
# p.asmPrint()
