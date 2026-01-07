import json
import os
EDITMODE = False

unique_mnemonics = []  # Lists all unique mnemonics
shortcutResolver = {}  # Carries a dict {shortcut:{arguments:mnemonic, }, }
instructions = {}	   # {Index:mnemonic, }

allArguments = {}         # {Index:arguments, }

pythonExportInstructions = {}  # {instruction: {"Binary":binary, "Arguments":arguments}, }
pythonExportShorthand = {}     # {shorthand: {arguments:mnemonic, }, }

FileSystemStructure = "Windows"
# GhostRoot =  "/home/flicker/Desktop/Ghost"

base_affectedFiles = {
	"Instruction Set.md": "Instruction Set.md",
	"OUTPUT-AssemblerDefs.py": "../Assembler/AssemblerDefs.py",
	"GHASM.sublime-syntax.template": "GHASM.sublime-syntax.template",
	"INPUT-GHASM.tmPreferences": "GHASM.tmPreferences",
	"INPUT-GHASM.sublime-build": "GHASM.sublime-build",
	"INPUT-cpu.cpp": "../Simulator/src/cpu.cpp",
	"OUTPUT-cpu.cpp": "../Simulator/src/cpu.cpp",
}

if FileSystemStructure == "Linux": # Places the Sublime files in their Linux location
	affectedFiles = {
		"OUTPUT-GHASM.sublime-syntax": os.path.expanduser("~/.config/sublime-text/Packages/User/GHASM.sublime-syntax"),
		"OUTPUT-GHASM.tmPreferences":  os.path.expanduser("~/.config/sublime-text/Packages/User/GHASM.tmPreferences"),
		"OUTPUT-GHASM.sublime-build":  os.path.expanduser("~/.config/sublime-text/Packages/User/GHASM.sublime-build"),
		"GhostRoot": os.path.expanduser("~/Desktop/Ghost"),
	}
elif FileSystemStructure == "Windows": # Places the Sublime files in their Windows location
	affectedFiles = {
		"OUTPUT-GHASM.sublime-syntax": os.path.expanduser(r"~\AppData\Roaming\Sublime Text\Packages\User\GHASM.sublime-syntax"),
		"OUTPUT-GHASM.tmPreferences":  os.path.expanduser(r"~\AppData\Roaming\Sublime Text\Packages\User\GHASM.tmPreferences"),
		"INPUT-GHASM.sublime-build":   "GHASM - Windows.sublime-build",
		"OUTPUT-GHASM.sublime-build":  os.path.expanduser(r"~\AppData\Roaming\Sublime Text\Packages\User\GHASM.sublime-build"),
		"GhostRoot": r"D:\\Ghost",
	}
elif FileSystemStructure == "Manual": # Allows the user to place the syntax file manually
	affectedFiles = {
		"OUTPUT-GHASM.sublime-syntax": "GHASM.sublime-syntax",
		"OUTPUT-GHASM.tmPreferences": None,
		"INPUT-GHASM.sublime-build": None, # Copying the sublime build requires GhostRoot
		"OUTPUT-GHASM.sublime-build": None,
		"OUTPUT-cpu.cpp": None,
		"GhostRoot": None,
	}
elif FileSystemStructure == "Custom": # Set your own file paths
	affectedFiles = {
		"Instruction Set.md": None, # Set EDITMODE explicetly to disble editing
		"OUTPUT-AssemblerDefs.py": None,
		"GHASM.sublime-syntax.template": None,
		"OUTPUT-GHASM.sublime-syntax": None, # Leave as none to disable output
		"INPUT-GHASM.tmPreferences": None,
		"OUTPUT-GHASM.tmPreferences": None, # Leave as none to disable output
		"INPUT-GHASM.sublime-build": None,
		"OUTPUT-GHASM.sublime-build": None, # Leave as none to disable output
		"INPUT-cpu.cpp": None,
		"OUTPUT-cpu.cpp": None, # Leave as none to disable output (Default: Same as above)
		"GhostRoot": None,
	}

for k, v in base_affectedFiles.items():
	if k not in affectedFiles.keys():
		affectedFiles[k] = v


def formatNumbers():
	global maxInstructionNumber, items, Index
	if "0b" not in items[0]:
		items[1] = ""
		return

	if "Register" in items[6]:
		while (Index % 0b100) != 0:
			# print(f"| 0b{Index:08b} | 0x{Index:02x} " + "|  " * (len(titles) - 2) + "|")
			if EDITMODE:
				dest.write(f"| 0b{Index:08b} | 0x{Index:02x} " + "|  " * (len(titles) - 2) + "|\n")
			Index += 1
		items[0] = f"0b{Index:08b}"
		items[0] = items[0][:-2] + "RR"
		items[1] = f"0x{Index:02x}"
		Index += 4
	else:
		items[0] = f"0b{Index:08b}"
		items[1] = f"0x{Index:02x}"
		Index += 1

def checkCommands():
	global unique_mnemonics, items, Index
	items[4] = items[4].upper()
	mne = items[4]
	if mne == "":
		return
	if mne in unique_mnemonics:
		print(f"Duplicate mnemonic of '{mne}' at Index {hex(Index)}")
		return
	if not mne.isalpha():
		print(f"Nonalphanumeric mnemonic of '{mne}' at Index {hex(Index)}")
		items[4] = ""
		items[5] = ""
		return
	unique_mnemonics.append(mne)
	instructionIndex = int(items[1], 16)
	if "Register" in items[6]:
		for i in range(4):
			instructions[instructionIndex + i] = mne + str(i)
			allArguments[instructionIndex + i] = items[6].split(", ")

	else:
		instructions[instructionIndex] = mne
		allArguments[instructionIndex] = items[6].split(", ")


def registerShortcuts():
	global items, Index
	items[5] = items[5].upper()
	mne = items[4]
	shortcut = items[5]
	arguments = items[6]
	if shortcut != "":
		if shortcut not in shortcutResolver.keys():
			shortcutResolver[shortcut] = {}
			pythonExportShorthand[shortcut] = {}
		if arguments == "":
			print(f"Argument missing at Index {hex(Index)}")
			return
		if arguments != "None":
			argList = arguments.split(", ")
			for i, arg in enumerate(argList):
				if i != 0 and arg == "Register":
					print(f"First argument must be the register, at Index {hex(Index)}")
					return
				if arg not in ["Register", "Value", "Address"]:
					print(f"Argument not in [Register, Type, Address]: {arg}, at Index {hex(Index)}")
					return
		shortcutResolver[shortcut][arguments] = mne
		pythonExportShorthand[shortcut][arguments.replace(',', '')] = mne
	if mne != "":
		pythonExportInstructions[mne] = {"Binary": items[0], "Arguments": arguments.replace(',', '')}


# MAIN (Don't feel like writing a function. Sue me.)
with open(affectedFiles["Instruction Set.md"], "r+" if EDITMODE else "r") as dest:
	Index = 0

	# Read file, reset for writing
	file_contents = dest.read()
	if EDITMODE:
		dest.seek(0)
		dest.truncate(0)
	lines = file_contents.split("\n")

	# Forward on the header
	titles = [x.strip() for x in lines[0].split("|")[1:-1]]
	if EDITMODE:
		dest.write("| " + " | ".join(titles) + " |\n")
		dest.write("| --- " * len(titles) + "|\n")

	# Scan Lines
	for line in lines[2:]:
		if "|" not in line:
			continue
		items = [x.strip() for x in line.split("|")[1:-1]]
		if "0b" in items[0] and "0x" in items[1] and all(x == "" for x in items[2:4]):
			print("Skipping", items[0])
			continue

		# formatNumbers()
		checkCommands()
		registerShortcuts()

		outputLine = "| " + " | ".join(items) + " |"
		if EDITMODE:
			dest.write(outputLine + "\n")

with open(affectedFiles["OUTPUT-AssemblerDefs.py"], 'w+') as f:
	f.write("Instructions = " + json.dumps(pythonExportInstructions, indent=4) + "\n")
	f.write("Shorthand = " + json.dumps(pythonExportShorthand, indent=4) + "\n")


with open(affectedFiles["GHASM.sublime-syntax.template"], 'r') as f:
	genSyntaxData = f.read()

genSyntaxData = genSyntaxData.replace(r"%INSTRUCTIONS%", '|'.join(unique_mnemonics))
genSyntaxData = genSyntaxData.replace(r"%SHORTHAND%", '|'.join(shortcutResolver.keys()))

with open(affectedFiles["OUTPUT-GHASM.sublime-syntax"], 'w+') as f:
	f.write(genSyntaxData)
if affectedFiles["OUTPUT-GHASM.tmPreferences"] is not None:
	with open(affectedFiles["INPUT-GHASM.tmPreferences"], 'r') as f1:
		with open(affectedFiles["OUTPUT-GHASM.tmPreferences"], 'w+') as f2:
			f2.write(f1.read())
if affectedFiles["OUTPUT-GHASM.sublime-build"] is not None:
	with open(affectedFiles["INPUT-GHASM.sublime-build"], 'r') as f1:
		with open(affectedFiles["OUTPUT-GHASM.sublime-build"], 'w+') as f2:
			f2.write(f1.read().replace("%GhostRoot%", affectedFiles["GhostRoot"]))

print("Done Reading" + (" and Revising!" if EDITMODE else "!"))



def RR(line="RR", register="RX"):
	if "RR" not in line:
		return line
	global mne
	if "X" in register:
		registerNumber = int(mne[-1])
		return line.replace("RR", register.replace("X", str(registerNumber)))
	return line.replace("RR", register)

def math(a, b, c=None, d=None):
	# (outcome, left, op, right) = (RR, RR, a, b), (a, a, b, c), or (a, b, c, d)
	if c is None:
		d = b
		c = a
		b = RR()
		a = RR()
	elif d is None:
		d = c
		c = b
		b = a


	return f"		{a} = {b} {c} {d};\n"


def cond(a, b, c=None):
	# Either (op, right) or (left, op, right)
	if c is None:
		c = b
		b = a
		a = RR()
	return f"		jump = {a} {b} {c};\n"


R0 = "R0"

def getArgument():
	return "getArgument()"
def getAtAddress(address):
	return f"getAtAddress({address})"
def getAtArgument():
	return getAtAddress(getArgument())
def getDD():
	return "DD"
def getAtDD():
	return getAtAddress(getDD())
def popStack():
	return "popFromStack()"
def getValue():
	return "value"

def setValue(value):
	return f"\t\tvalue = {value};\n"
def setAtAddress(address, value="value"):
	return f"\t\tsetValueAtAddress({value}, {address});\n"
def setRR(value, register="RR"):
	return f"\t\t{RR(register)} = {value};\n"
def setDD(value):
	return f"\t\tDD = {value};\n"
def setAtDD(value):
	return setAtAddress("DD", value)
def pushStack(value):
	return f"\t\tpushToStack({value});\n"
def jumpTo(address, noAdd=False):
	return f"\t\tPC = {address}{'' if noAdd else '-1'}+offsetRegister;\n"
def conditional(interior):
	lines = len(interior.split("\n"))
	if lines == 2:
		return "\t\tif(jump)\n\t" + interior
	else:
		return "\t\tif(jump) {\n\t" + "\n\t".join(interior.split("\n")) + "\t}\n"
def debugOut(value):
	return f"\t\tstd::cout << \"0x\" << std::hex << std::setw(4) << std::setfill('0') << {value} << std::endl;\n"
def debugOutChar(value):
	# return f"\t\tstd::cout << (char){value};\n\t\tif (flushDebugChar)\n\t\t\tstd::cout << std::endl;\n"
	return "\t\tvalue = " + value + ";\n\t\tif (value != '\\n') \n\t\t\tstd::cout << (char)value;\n\t\telse if (flushDebugChar || value == '\\n')\n\t\t\tstd::cout << std::endl;\n"
def setOffset(value):
	return f"\t\toffsetRegister = {value};\n"

with open(affectedFiles["INPUT-cpu.cpp"], 'r') as f:
	cppFile = f.read()

debuggingString1 = "const std::string InstructionDebugging[0x100] {"
debuggingString1Pos = cppFile.find(debuggingString1) + len(debuggingString1)
debuggingString1End = cppFile[debuggingString1Pos:].find("}") + debuggingString1Pos

cppFile = cppFile[:debuggingString1Pos] + (", ".join('"' + instructions.get(i, "NONE") + '"' for i in range(0x100))) + cppFile[debuggingString1End:]

debuggingString2 = "const int InstructionDebuggingNumArgs[0x100] {"
debuggingString2Pos = cppFile.find(debuggingString2) + len(debuggingString2)
debuggingString2End = cppFile[debuggingString2Pos:].find("}") + debuggingString2Pos

cppFile = cppFile[:debuggingString2Pos] + (", ".join([str(len([y for y in x if y not in ["Register", "None"]])) for x in [allArguments.get(i, ['None']) for i in range(0x100)]])) + cppFile[debuggingString2End:]

instructionsStartString = "void cpu::executeFunction(unsigned short instruction) {\n\tswitch (instruction) {\n"
instructionsStart = cppFile.find(instructionsStartString) + len(instructionsStartString)
instructionsEndString = "\n\tdefault:"
instructionsEnd = cppFile[instructionsStart:].find(instructionsEndString) + instructionsStart+1

allInstrutions = ""

for i in range(0, 0x100):
	mne = instructions.get(i, "Unused")
	allInstrutions += f"\t// case 0x{i:02x}:\n" if mne == 'Unused' else f"\tcase 0x{i:02x}: // {mne}\n"
	content = ""
	if mne == "NOP" or mne == "Unused":
		pass
	elif mne == "MVAA":
		content = setValue(getAtArgument()) + setAtAddress(getArgument())
	elif mne == "DDV":
		content = setDD(getArgument())
	elif mne == "DDA":
		content = setDD(getAtArgument())
	elif mne.startswith("DDR"):
		content = setDD(RR())
	elif mne.startswith("LDV"):
		content = setRR(getArgument())
	elif mne.startswith("LDA"):
		content = setRR(getAtArgument())
	elif mne.startswith("LDD"):
		content = setRR(getAtDD())
	elif mne.startswith("STR"):
		content = setAtAddress(getArgument(), RR())
	elif mne.startswith("STAR"):
		content = setAtAddress(RR(), getArgument())
	elif mne == "STV":
		content = setValue(getArgument()) + setAtAddress(getArgument()) 
	elif mne == "STDV":
		content = setAtDD(getArgument())
	elif mne == "MVDD":
		content = setAtAddress(getArgument(), getAtDD())  # setAtAddress(address, value="value"):
	elif mne == "INT":
		content = setValue(getArgument()) + """\t\tif (value > 0x5f || AllowedInterrupts.find(value) == AllowedInterrupts.end()) {
\t\t\tstd::cout << "ERR: Invalid interrupt 0x" << std::hex << std::setw(2) << std::setfill('0') << value << std::endl;
\t\t\thalted = true;
\t\t} else {
\t\t\tpushToStack(PC-offsetRegister);
\t\t\tPC = MEMORY[0xaf00 + value]-1;
\t\t}
"""
	elif mne.startswith("STDR"):
		content = setAtDD(RR())
	elif mne.startswith("SHLV"):
		content = math("<<", getArgument())
	elif mne.startswith("SHLA"):
		content = math("<<", getAtArgument())
	elif mne.startswith("SHLR"):
		content = math(R0, "<<", RR())
	elif mne.startswith("SHRV"):
		content = math(">>", getArgument())
	elif mne.startswith("SHRA"):
		content = math(">>", getAtArgument())
	elif mne.startswith("SHRR"):
		content = math(R0, ">>", RR())
	elif mne.startswith("ADDV"):
		content = math("+", getArgument())
	elif mne.startswith("ADDA"):
		content = math("+", getAtArgument())
	elif mne.startswith("ADDR"):
		content = math(R0, "+", RR())
	elif mne.startswith("SUBV"):
		content = math("-", getArgument())
	elif mne.startswith("SUBA"):
		content = math("-", getAtArgument())
	elif mne.startswith("SUBR"):
		content = math(R0, "-", RR())
	elif mne.startswith("SBRV"):
		content = math(RR(), getArgument(), "-", RR())
	elif mne.startswith("SBRA"):
		content = math(RR(), getAtArgument(), "-", RR())
	elif mne.startswith("SBRR"):
		content = math(R0, RR(), "-", R0)
	elif mne.startswith("NOT"):
		content = f"\t\t{RR()} = ~{RR()};\n"
	elif mne.startswith("NEG"):
		content = f"\t\t{RR()} = -{RR()};\n"
	elif mne == "INCD":
		content = f"\t\tDD++;\n"
	elif mne == "DECD":
		content = f"\t\tDD--;\n"
	elif mne.startswith("INC"):
		content = f"\t\t{RR()}++;\n"
	elif mne.startswith("DEC"):
		content = f"\t\t{RR()}--;\n"
	elif mne.startswith("SHLO"):
		content = math("<<", "1")
	elif mne.startswith("SHRO"):
		content = math(">>", "1")
	elif mne.startswith("ANDV"):
		content = math("&", getArgument())
	elif mne.startswith("ANDA"):
		content = math("&", getAtArgument())
	elif mne.startswith("ANDR"):
		content = math(R0, RR(), "&", R0)
	elif mne.startswith("ORV"):
		content = math("|", getArgument())
	elif mne.startswith("ORA"):
		content = math("|", getAtArgument())
	elif mne.startswith("ORR"):
		content = math(R0, RR(), "|", R0)
	elif mne.startswith("XORV"):
		content = math("^", getArgument())
	elif mne.startswith("XORA"):
		content = math("^", getAtArgument())
	elif mne.startswith("XORR"):
		content = math(R0, RR(), "^", R0)
	elif mne.startswith("LDZ"):
		content = f"\t\tR0 = {RR()};\n"
	elif mne.startswith("STZ"):
		content = f"\t\t{RR()} = R0;\n"
	elif mne.startswith("PSHR"):
		content = pushStack(RR())
	elif mne.startswith("POPR"):
		content = setRR(popStack())
	elif mne == "PSHA":
		content = pushStack("R0") + pushStack("R1") + pushStack("R2") + pushStack("R3")
	elif mne == "POPA":
		content = setRR(popStack(), "R3") + setRR(popStack(), "R2") + setRR(popStack(), "R1") + setRR(popStack(), "R0")
	elif mne == "LDSP":
		content = f"\t\tR0 = SP-offsetRegister;\n"
	elif mne == "STSP":
		content = f"\t\tSP = R0+offsetRegister;\n"
	elif mne == "CEZA":
		content = cond(getAtArgument(), "==", "0")
	elif mne == "CNZA":
		content = cond(getAtArgument(), "!=", "0")
	elif mne.startswith("CEZR"):
		content = cond("==", "0")
	elif mne.startswith("CNZR"):
		content = cond("!=", "0")
	elif mne.startswith("CEV"):
		content = cond("==", getArgument())
	elif mne.startswith("CEA"):
		content = cond("==", getAtArgument())
	elif mne.startswith("CNV"):
		content = cond("!=", getArgument())
	elif mne.startswith("CNA"):
		content = cond("!=", getAtArgument())
	elif mne.startswith("CLTV"):
		content = cond("<", getArgument())
	elif mne.startswith("CLTA"):
		content = cond("<", getAtArgument())
	elif mne.startswith("CGTV"):
		content = cond(">", getArgument())
	elif mne.startswith("CGTA"):
		content = cond(">", getAtArgument())
	elif mne == "JMPA":
		content = jumpTo(getArgument())
	elif mne == "JMPD":
		content = jumpTo(getDD())
	elif mne == "CALA":
		content = pushStack("PC+1-offsetRegister") + jumpTo(getArgument())
	elif mne == "CALD":
		content = pushStack("PC-offsetRegister") + jumpTo(getDD())
	elif mne == "RET":
		content = jumpTo(popStack(), noAdd=True)
	elif mne == "JPCA":
		content = setValue(getArgument()) + conditional(jumpTo(getValue()))
	elif mne == "JPCD":
		content = conditional(jumpTo(getDD()))
	elif mne == "CLCA":
		content = setValue(getArgument()) + conditional(pushStack("PC-offsetRegister") + jumpTo(getValue()))
	elif mne == "CLCD":
		content = conditional(pushStack("PC-offsetRegister") + jumpTo(getDD()))
	elif mne == "RETC":
		content = conditional(jumpTo(popStack(), noAdd=True))
	elif mne == "BRK":
		content = "\t\tstd::cout << \"\\nCPU BREAK\" << std::endl;\n"
		content += "\t\tbroken = true;\n"
	elif mne == "HLT":
		content = "\t\tstd::cout << \"\\nCPU HALT\" << std::endl;\n"
		content += "\t\thalted = true;\n"
	elif mne.startswith("DBGR"):
		content = debugOut(RR())
	elif mne == "DBGV":
		content = debugOut(getArgument())
	elif mne == "DBGA":
		content = debugOut(getAtArgument())
	elif mne == "DBCA":
		content = debugOutChar(getAtArgument())
	elif mne == "DBCV":
		content = debugOutChar(getArgument())
	elif mne.startswith("DBCR"):
		content = debugOutChar(RR())
	elif mne.startswith("ADOR"):
		content = setOffset(RR())
	elif mne == "ADOV":
		content = setOffset(getArgument())
	elif mne == "ADOA":
		content = setOffset(getAtArgument())
	elif mne == "IDIS":
		content = "\t\tinteruptHandling = false;\n"
	elif mne == "IEN":
		content = "\t\tinteruptHandling = true;\n"
	elif mne == "AOR":
		content = f"\t\tR0 = offsetRegister;\n"
	elif mne == "CPSH":
		content = pushStack('jump')
	elif mne == "CPOP":
		content = f"\t\tjump = {popStack()};\n"
	else:
		print(mne)
		raise NotImplementedError
	# f.write(content)
	# f.write("" if mne == 'Unused' else "		break;\n")
	allInstrutions += content
	allInstrutions += "" if mne == 'Unused' else "		break;\n"


cppFile = cppFile[:instructionsStart] + allInstrutions + cppFile[instructionsEnd:]

if affectedFiles["OUTPUT-cpu.cpp"] is not None:
	with open(affectedFiles["OUTPUT-cpu.cpp"], 'w+') as f:
		f.write(cppFile)

print("Done Writing!")
