import sys
import os
import re

debugging = {
	"Pass Notifs": False,
	"Export Notifs": True,
	"Rollover Warns": True,
	"Halt Warns": True,
	"Assumptions": False,
	"Midpoint Ouput": False,
	"Label Outputs": False,
	"Defs Outputs": False,
}

def clearComments(line):
	if assemblerDefs.Comment in line:
		outLine = ""
		for char in line:
			if char == ';':
				break
			outLine += char
		return outLine.strip()
	return line

def argumentTypes(line):
	if assemblerDefs.Label in line:
		line = " ".join(line.split(assemblerDefs.Label)[1:])
	if line == "":
		return []
	if line.strip()[0] == assemblerDefs.Data:
		if line.strip().startswith(".ds"):
			amountOfChars = len(line.replace(".ds", "").strip().replace('"', ""))
			# print("In line", line, "there are", amountOfChars, "characters")
			return ["Value"] * amountOfChars
		return ["Value"]
	words = line.strip().split(" ")

	types = []
	for word in words:
		if word in list(assemblerDefs.Instructions.keys()):
			types.append("Instruction")
		elif word.startswith(assemblerDefs.Address):
			types.append("Address")
		elif word in assemblerDefs.Registers:
			types.append("RR")
		elif word != "":
			types.append("Value")
	return types

def prettyOrList(listOfWords): 
	# ['a']				=> "a"
	# ['a', 'b']		=> "a or c"
	# ['a', 'b', 'c']	=> "a, b, or c"
	if len(listOfWords) == 0:
		return ""
	elif len(listOfWords) == 1:
		return str(listOfWords[0])
	elif len(listOfWords) == 2:
		return str(listOfWords[0]) + " or " + str(listOfWords[1])
	else:
		outString = ""
		for wordNum, word in enumerate(listOfWords):
			if wordNum == len(listOfWords)-1:
				outString += ("or " + word)
				break
			outString += (word + ", ")
		return outString

def resolveShorthand(line):
	words = line.strip().split(" ")
	if words[0] in assemblerDefs.Shorthand.keys():
		ArgumentTypes = argumentTypes(" ".join(words[1:]))
		ArgumentTypesString = " ".join(ArgumentTypes)
		if ArgumentTypesString in assemblerDefs.Shorthand[words[0]].keys():
			words[0] = assemblerDefs.Shorthand[words[0]][ArgumentTypesString]
			return " ".join(words)
		else:
			print(f"\nX Error resolving shorthand command '{words[0]}' with arguments [{', '.join(ArgumentTypes)}], on line {lineNumber+1}")
			listOfShorthandArguments = list(assemblerDefs.Shorthand[words[0]].keys())
			print(f"Expected types are: {prettyOrList(['[' + ', '.join(typeList.split(' ')) + ']' for typeList in listOfShorthandArguments])}")
			sys.exit()
	return line

def validateArguments(line):
	words = line.strip().split(" ")
	# Exceptions, should not be instructions
	if line.strip() == '': # Empty
		return line
	if assemblerDefs.Label in line: # Label
		return line
	if line.startswith("#DEF"): # Definition
		return line
	if line.startswith("#INC"): # Include
		return line
	if assemblerDefs.Data in line: # Data
		return line
	# Validating
	if words[0] in assemblerDefs.Instructions.keys():
		ArgumentTypes = argumentTypes(" ".join(words[1:]))
		ArgumentTypesString = " ".join(ArgumentTypes)
		if not ArgumentTypesString == assemblerDefs.Instructions[words[0]]['Arguments']:
			print(f"\nX Error validating command '{words[0]}' with arguments [{', '.join(ArgumentTypes)}]")
			expectedArguments = assemblerDefs.Instructions[words[0]]['Arguments']
			print(f"Expected types are: [{', '.join(expectedArguments.split(' '))}]")
			sys.exit()
	else:
		print(f"\nX Error resolving command '{words[0]}'")
		sys.exit()

def resolveChars(line):
	if not line.startswith(".dc"):
		words = line.replace("' '", str(ord(" "))).strip().split(" ")
	else:
		words = line.strip().split(" ")
	for wordNumber, word in enumerate(words):
		if len(word) == 3 and word[0] == word[2] == "'" and not line.startswith(".dc"):
			# print(line)
			words[wordNumber] = intToHexString(ord(word[1]))
			continue
	line = " ".join(words)
	return line

def recordDefs(line):
	if line.startswith("#DEF"):
		words = line.split()
		definitions[words[1]] = int(words[2], 0)
		return ""
	return line

def recordLabels(line, position):
	if line.startswith(assemblerDefs.Data):
		return line
	if assemblerDefs.Label in line:
		labels[line.split(assemblerDefs.Label)[0]] = position
		return line.split(assemblerDefs.Label)[-1].strip()
	return line


def intToHexString(num):
	if num > 0xffff and debugging["Rollover Warns"]:
		print(f"! Found the value {str(hex(num))}, which is greater than 0xffff. Rolling to {'0x' + ('0000' + str(hex(num))[2:])[-4:]}")
	return "0x" + (("0"*4) + str(hex(num))[2:])[-4:]

def intToBinString(num, prefix=True):
	if num > 0xffff and debugging["Rollover Warns"]:
		print(f"! Found the value {str(hex(num))}, which is greater than 0xffff. Rolling to {'0x' + ('0000' + str(hex(num))[2:])[-4:]}")
	return ("0b" if prefix else "") + (("0"*16) + str(bin(num))[2:])[-16:]

def isValidFinalHex(hexString):
	if len(hexString) != 6:
		return False
	if not hexString.startswith("0x"):
		return False
	for character in hexString[2:]:
		if character not in '0123456789abcdef':
			return False
	return True

def assemble(file="main.ghasm"):
	global labels, definitions, lineNumber
	labels = {}
	definitions = {}
	position = 0
	print(f"GhostDefs {assemblerDefs.GhostDefsVersion}")
	print(f"- Assembling {file}")
	with open(file, 'r') as f:
		allData = f.read()
	if not "HLT" in allData and debugging["Halt Warns"]:
		print(f"! No 'HLT' instruction found: may result in undefined behavior")
	linesList = allData.split("\n")
	if debugging["Pass Notifs"]:
		print("- Pass 1: Remove Comments, Record labels, Record Defs, Resolve Shorthand, Check Syntax")
	for lineNumber, line in enumerate(linesList):
		line = line.strip()
		if line.startswith("#INC"):
			if len(line.split(" ")) != 2:
				print("X Include requires exactly 1 argument: a file name")
				sys.exit()
			incFile = line.split(" ")[1]
			if not incFile.endswith(".hex"):
				print("X Include requires file to end in .hex, you gave:", incFile)
				sys.exit()
			print("- Including hex file", incFile)
			try:
				with open(incFile, 'r') as f:
					line = "#INC" + (" ".join(f.read().split()))
			except OSError:
				print("X Include could not open the provided file:", incFile)
				sys.exit()
				
			linesList[lineNumber] = line
		line = clearComments(line)
		line = resolveChars(line)
		line = resolveShorthand(line)
		validateArguments(line)
		line = recordLabels(line, position)
		line = recordDefs(line)

		position += sum([assemblerDefs.TypeLengths[typeOfItem] for typeOfItem in argumentTypes(line)])

		linesList[lineNumber] = line

	if debugging["Label Outputs"]:
		for k,v in labels.items():
			print("-", k, v)

	if debugging["Defs Outputs"]:
		for k,v in definitions.items():
			print("-", k, v)

	if debugging["Midpoint Ouput"]:
		 with open("Midpoint.txt", 'w+') as f:
		 	f.write("\n".join(linesList))
	
	if debugging["Pass Notifs"]:
		print("- Pass 2: Resolve Labels, Resolving Defs, Resolve Registers, Do Math, To hexadecimal!")
	for lineNumber, line in enumerate(linesList):
		if line.strip() == "":
			continue
			
		for label in labels.keys():
			if label in line:
				pat = r"(\s\$?)(" + label + r")(?=[\s+\-\/*]|$)"
				line = re.sub(pat, r"\g<1>" + str(intToHexString(labels[label])), line)
			
		for definition in definitions.keys():
			if definition in line:
				pat = r"(\s\$?)(" + definition + r")(?=[\s+\-\/*]|$)"
				line = re.sub(pat, r"\g<1>" + str(intToHexString(definitions[definition])), line)

		if line.strip()[0] == assemblerDefs.Data:
			dataTypeWord = line.split(" ")[0].strip()
			dataType = {".db":"Bin",".dh":"Hex",".dd":"Dec",".dc":"Char",".ds":"String"}.get(dataTypeWord, None)
			if dataType == None:
				print(f"\nX Error resolving data type of '{word}' on line {lineNumber+1}")
				sys.exit()
			val = "".join(line.split(" ")[1:])
			if dataType == "Bin":
				line = intToHexString(eval(val))
			if dataType == "Dec":
				line = intToHexString(eval(val))
			if dataType == "Hex":
				line = intToHexString(eval(val))
			if dataType == "Char":
				val = " ".join(line.split(" ")[1:])
				if len(val) != 3 or (val[0] != "'" or val[2] != "'"):
					print(f"\nX Error resolving char {val} on line {lineNumber+1}")
					sys.exit()
				line = intToHexString(ord(val[1]))
			if dataType == "String":
				val = " ".join(line.split(" ")[1:])
				if not val[0] == val[-1] == '"':
					print(f"\nX Error resolving string {val} on line {lineNumber+1}")
					sys.exit()
				line = " ".join([intToHexString(ord(ch)) for ch in val[1:-1]])
		
		if line.startswith("#INC"):
			line = line.replace("#INC", "")
			linesList[lineNumber] = line
			continue
		
		words = line.split(" ")
		for wordNumber, word in enumerate(words):
			if word in assemblerDefs.Registers:
				words[wordNumber] = ""
				line = " ".join([x for x in words if x != ""])
				continue
				
			if len(word) == 3 and word[0] == word[2] == "'":
				words[wordNumber] = intToHexString(ord(word[1]))
				line = " ".join([x for x in words if x != ""])
				continue
					
			word = word.replace(assemblerDefs.Address, "")
			if word.strip() == "":
				continue
			if any([(op in word) for op in "-+/*"]):
				word = intToHexString(eval(word))

			if word in list(assemblerDefs.Instructions.keys()):
				Binary = assemblerDefs.Instructions[word]["Bin"]
				if "RR" in Binary:
					Binary = Binary.replace("RR", str(bin(assemblerDefs.Registers.index(words[wordNumber+1])))[2:].zfill(2))
				word = intToHexString(int(Binary, 2))
			
			if not isValidFinalHex(word):
				try:
					newWord = intToHexString(int(word, 0))
					if debugging["Assumptions"]:
						print(f"! Assumed token '{word}' to '{newWord}'")
					word = newWord
				except ValueError:
					print(f"\nX Error resolving token '{word}' on line {lineNumber+1}, word {wordNumber+1}")
					sys.exit()


			words[wordNumber] = word.strip()
			line = " ".join([x for x in words if x != ""])		

		linesList[lineNumber] = line
	saveFileName = ".".join(file.split(".")[:-1])
	writeData(saveFileName, "\n".join(linesList), formatTypes=["Hex", "WhitespaceHex", "HexPerLine"])
	# return saveFileName
	return " ".join(linesList)
	
def writeData(fileName, fileData, formatTypes = ["Hex"]):
	if "WhitespaceHex" in formatTypes:
		outString = str(fileData)
		if debugging["Export Notifs"]:
			print("- Exporting to .w.hex")
		with open(fileName + ".w.hex", 'w+') as f:
			f.write(outString)
	if "HexPerLine" in formatTypes:
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += byte + "\n"
		if debugging["Export Notifs"]:
			print("- Exporting to .l.hex")
		with open(fileName + ".l.hex", 'w+') as f:
			f.write(outString)
	if "Hex" in formatTypes:
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += byte + ("\n" if bytePos%8==7 else " ")
		if debugging["Export Notifs"]:
			print("- Exporting to .hex")
		with open(fileName + ".hex", 'w+') as f:
			f.write(outString)
	if "Binary" in formatTypes:
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += intToBinString(int(byte, 16)) + ("\n" if bytePos%8==7 else " ")
		if debugging["Export Notifs"]:
			print("- Exporting to .bin")
		with open(fileName + ".bin", 'w+') as f:
			f.write(outString)
	if "BinaryDict" in formatTypes:
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += f'"{intToBinString(bytePos, prefix=False)}": "{intToBinString(int(byte, 16), prefix=False)}",\n'
		if debugging["Export Notifs"]:
			print("- Exporting to .b.dict")
		with open(fileName + ".b.dict", 'w+') as f:
			f.write(outString)
	if "DecimalDict" in formatTypes:
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += f'{bytePos}: {int(byte, 16)},\n'
		if debugging["Export Notifs"]:
			print("- Exporting to .d.dict")
		with open(fileName + ".d.dict", 'w+') as f:
			f.write(outString)
	print("- The total file size is",len(fileData.split()),"bytes")



if __name__ == '__main__':
	print("Ghost assembler for GHASM")
	import assemblerDefs
	args = sys.argv[1:]
	if len(args) == 0:
		exportedFile = assemble()
	else:
		exportedFile = assemble(args[0])