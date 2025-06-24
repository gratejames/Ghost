mc_lookup = {
	"from": {
		"R0": "0",
		"R1": "1",
		"R2": "2",
		"R3": "3",
		"PC": "4",
		"VR": "5",
		"AR": "6",
		"MD": "7",
		"Y":  "8",
		"AO": "9",
		"SP": "a",
		"Cond": "b",
		"__": "c",
		"__": "d",
		"Math": "e",
		"Other": "f",
	},
	"to": {
		"R0": "0",
		"R1": "1",
		"R2": "2",
		"R3": "3",
		"PC": "4",
		"VR": "5",
		"AR": "6",
		"MW": "7",
		"MA": "8",
		"A":  "9",
		"B":  "a",
		"AO": "b",
		"DBG":  "c",
		"DBGC": "d",
		"MPC": "e",
		"__": "f",
	},
	"macros": [
		("PC++", "PC->A,Math0010,Y->PC"),
	]
}

def listTryGet(li, i, els):
	if len(li) > i:
		return li[i]
	else:
		return els

def parseMicrocode(strIn, binStr):
	for macro, expanded in mc_lookup["macros"]:
		strIn = strIn.replace(macro, expanded)
	output = []
	for token in [x.strip() for x in strIn.split(',') if x.strip() != ""]:
		if token == 'X':
			output.append("0xff")
		elif token == 'Halt':
			output.append("0xfe")
		elif token == 'XC':
			output.append("0xfd")
		elif token == 'XIC':
			output.append("0xfc")
		elif token[0:5] == "Other":
			output.append(f"0xf{str(hex(int(token[5:9],2)))[2]}")
		elif token[0:4] == "Math":
			output.append(f"0xe{str(hex(int(token[4:8],2)))[2]}")
		elif "->" in token:
			a, b = token.split("->")
			a = mc_lookup["from"][a]
			b = mc_lookup["to"][b]
			output.append(f"0x{a}{b}")
		else:
			print(f"Token error {token}")
	if len(output) > 16:
		print(f"MC overflow: {binStr} at {len(output)}")
		return " ".join(["0xff"] * 16)
	return " ".join(listTryGet(output, i, "....") for i in range(16))
	# return " ".join(listTryGet(output, i, "0x00") for i in range(16))


with open("../Docs/Hmm Microcode.md", "r") as f:
	docs = f.read()

fw = open("mc_rom.txt", "w+")
fileIndex = 0

numberOfInstructions = 0
numberWithMC = 0

for line in docs.split("\n"):
	cols = [k for k in line.split("|") if k != ""]
	if len(cols) != 9 or "0b" not in cols[0]:
		continue
	numberOfInstructions += 1
	binStr = cols[0]
	microcodeStr = cols[7]
	if microcodeStr.strip() == "":
		print("Instruction w/o mc: ", binStr)
		continue

	index = int(binStr.replace("RR", "00"), 2)-1

	if microcodeStr.strip()[-1] != "X" and index+1 != 0:
		print("MC w/o X: ", binStr)

	while fileIndex < index:
		fileIndex += 1
		fw.write(" ".join(["0xff"] * 16) + "\n")
		
	if "RR" in binStr:
		for i in range(4):
			rr = f"{i:02b}"
			newBinStr = binStr.replace("RR", rr)
			newMCStr = microcodeStr.replace("RR", f"R{i}")
			index = int(newBinStr, 2)
			microcode = parseMicrocode(newMCStr, binStr)
			fw.write(microcode.replace("....", "0xff") + "\n")
			# print(f"{index: 4}", newMCStr, microcode)
			fileIndex = index
	else:
		index = int(binStr, 2)
		microcode = parseMicrocode(microcodeStr, binStr)
		fw.write(microcode.replace("....", "0xff") + "\n")
		# print(f"{index: 4}", microcodeStr, microcode)
		fileIndex = index
	numberWithMC += 1
fw.close()

print(f"Implemented instructions: {numberWithMC}/{numberOfInstructions}", end=" ")
if numberOfInstructions != 0:
	print(f"{numberWithMC/numberOfInstructions:.2f}")
else:
	print()