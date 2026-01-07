import nodes


def flatten(functions):
    arr = []
    for name, f in functions.items():
        lifetimes_names = []
        f.indent = 0
        arr.append(f)
        anames = [a.register for a in f.arguments]
        lifetimes_names += anames
        for i, a in enumerate(f.allocs):
            a = nodes.lateAlloc(i, a)
            a.indent = 1
            arr.append(a)
        for b in f.blocks:
            blockarr = []
            b.label.indent = 1
            arr.append(b.label)
            recursive_flatten(b.final, b, blockarr)
            arr += blockarr
    return arr


def recursive_flatten(node, block, arr):
    match node:
        case nodes.Call():
            for a in node.callargs:
                recursive_flatten(a, block, arr)
        case nodes.Ret():
            recursive_flatten(node.pre_node, block, arr)
        case nodes.Load():
            recursive_flatten(node.pointer, block, arr)
        case nodes.Store():
            recursive_flatten(node.pre_node, block, arr)
        case nodes.Branch():  # Terminal Node
            pass
        case nodes.BranchCond():
            recursive_flatten(node.cmp, block, arr)
        case nodes.StackVar():  # Terminal Value
            return
        case nodes.Constant():  # Terminal Value
            return
        case nodes.GlobalReference():  # Terminal Value
            return
        case nodes.FunctionDefArgument():  # Terminal Node
            pass
        case nodes.BiOp():
            recursive_flatten(node.op1, block, arr)
            recursive_flatten(node.op2, block, arr)
        case nodes.Icmp():
            recursive_flatten(node.op1, block, arr)
            recursive_flatten(node.op2, block, arr)
        case nodes.RegisterReference():
            if node.name in block.registers:
                recursive_flatten(block.registers[node.name], block, arr)
                return
            else:
                print("Failed to match register reference", node)
                exit()
        case nodes.Void():
            return
        case _:
            print("Failed to flatten node", node)
            exit()
    if node is block.final:
        for pointer, chain in list(block.memoryeffects.items())[::-1]:
            chainarr = []
            for link in chain[::-1]:
                if not link.visited:
                    recursive_flatten(link, block, chainarr)
                    break
            for i, c in enumerate(chainarr):
                arr.insert(i, c)

        unmatched_chain_elements = sum(
            [
                len([link for link in chain if not link.visited])
                for chain in block.memoryeffects.values()
            ]
        )
        if unmatched_chain_elements != 0:
            print(
                "Chain unvisited:",
                unmatched_chain_elements,
                [
                    [link for link in chain if not link.visited]
                    for chain in block.memoryeffects.values()
                ],
            )
            exit()
    node.visited = True
    node.indent = 2
    arr.append(node)
