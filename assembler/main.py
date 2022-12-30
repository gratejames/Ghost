import sys
import os
import re

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

def resolveShorthand(line):
	words = line.strip().split(" ")
	if words[0] in assemblerDefs.Shorthand.keys():
		ArgumentTypes = argumentTypes(" ".join(words[1:]))
		ArgumentTypesString = " ".join(ArgumentTypes)
		if ArgumentTypesString in assemblerDefs.Shorthand[words[0]].keys():
			words[0] = assemblerDefs.Shorthand[words[0]][ArgumentTypesString]
			return " ".join(words)
		else:
			print(f"\nX Error resolving shorthand command '{words[0]}' with arguments [{', '.join(ArgumentTypes)}]")
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

def recordLabels(line):
	if assemblerDefs.Label in line:
		labels[line.split(assemblerDefs.Label)[0]] = position
		return line.split(assemblerDefs.Label)[-1].strip()
	return line

def intToHexString(num):
	if num > 65535:
		print(f"! Found the value {str(hex(num))}, which is greater than 0xffff. Rolling to {'0x' + ('0000' + str(hex(num))[2:])[-4:]}")
	return "0x" + (("0"*4) + str(hex(num))[2:])[-4:]

def intToBinString(num, prefix=True):
	if num > 65535:
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
	global position, labels
	labels = {}
	position = 0
	print(f"GhostDefs {assemblerDefs.GhostDefsVersion}")
	print(f"- Assembling {file}")
	with open(file, 'r') as f:
		allData = f.read()
	if not "HLT" in allData:
		print(f"! No 'HLT' instruction found: may result in undefined behavior")
	linesList = allData.split("\n")
	
	print("- Pass 1: Remove Comments, Record labels, Resolve Shorthand, Check Syntax")
	for lineNumber, line in enumerate(linesList):
		line = line.strip()
		line = clearComments(line)
		line = resolveShorthand(line)
		validateArguments(line)
		line = recordLabels(line)

		position += sum([assemblerDefs.TypeLengths[typeOfItem] for typeOfItem in argumentTypes(line)])

		linesList[lineNumber] = line

	print("-", labels)

	# with open("Pass1.txt", 'w+') as f:
	# 	f.write("\n".join(linesList))
	
	print("- Pass 2: Resolve Labels, Resolve Registers, Do Math, To hexadecimal!")
	for lineNumber, line in enumerate(linesList):
		if line.strip() == "":
			continue
		for label in labels.keys():
			if label in line:
				pat = r"(\s\$?)(" + label + r")(?=[\s+\-\/*]|$)"
				line = re.sub(pat, r"\g<1>" + str(intToHexString(labels[label])), line)

		if line.strip()[0] == assemblerDefs.Data:
			dataTypeWord = line.split(" ")[0].strip()
			dataType = {".db":"Bin",".dh":"Hex",".dd":"Dec"}.get(dataTypeWord, None)
			if dataType == None:
				print(f"\nX Error resolving data type of '{word}' on line {lineNumber+1}")
				sys.exit()
			val = "".join(line.split(" ")[1:])
			if dataType == "Bin":
				line = intToHexString(int(val, 2))
			if dataType == "Dec":
				line = intToHexString(int(val, 10))
			if dataType == "Hex":
				line = intToHexString(int(val, 16))

		words = line.split(" ")
		for wordNumber, word in enumerate(words):
			if word in assemblerDefs.Registers:
				words[wordNumber] = ""
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
					Binary = Binary.replace("RR", str(bin(int(words[wordNumber+1])))[2:].zfill(2))
				word = intToHexString(int(Binary, 2))

			if not isValidFinalHex(word):
				print(f"\nX Error resolving token '{word}' on line {lineNumber+1}, word {wordNumber+1} ({line})")
				sys.exit()


			words[wordNumber] = word.strip()
			line = " ".join([x for x in words if x != ""])
		linesList[lineNumber] = line


		

		linesList[lineNumber] = line
	saveFileName = ".".join(file.split(".")[:-1]) + ".hex"
	writeData(saveFileName, "\n".join(linesList))#, formatType="DecimalDict")
	return saveFileName
	
def writeData(fileName, fileData, formatType = "Hex"):
	if formatType == "WhitespaceHex":
		outString = fileData
	elif formatType == "Hex":
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += byte + ("\n" if bytePos%8==7 else " ")
	elif formatType == "Binary":
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += intToBinString(int(byte, 16)) + ("\n" if bytePos%8==7 else " ")
	elif formatType == "BinaryDict":
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += f'"{intToBinString(bytePos, prefix=False)}": "{intToBinString(int(byte, 16), prefix=False)}",\n'
	elif formatType == "DecimalDict":
		outString = ""
		for bytePos, byte in enumerate(fileData.split()):
			outString += f'{bytePos}: {int(byte, 16)},\n'

	with open(fileName, 'w+') as f:
		f.write(outString)


if __name__ == '__main__':
	print("Ghost assembler for GHASM")
	import assemblerDefs
	args = sys.argv[1:]
	if len(args) == 0:
		exportedFile = assemble()
	else:
		exportedFile = assemble(args[0])