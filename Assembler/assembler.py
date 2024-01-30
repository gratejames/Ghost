#!/usr/bin/env python3
import sys
import re
import AssemblerDefs

class assembler:
	TypeLengths = {"Value": 1, "Address": 1, "Instruction": 1, "Register": 0}  # Length in bytes of each type used below

	def __init__(self):
		self.fileContents = ""
		self.fileName = "String Input"
		self.definitions = {}
		self.shares = []
		self.macros = {}
		self.position = 0
		self.lineNumber = 0
		self.shareall = False
		pass

	def die(self, message):
		print(message)
		sys.exit()

	def loadFile(self, fileName):
		self.fileName = fileName
		with open(fileName, 'r') as f:
			self.fileContents = f.read()

	def clearComments(self, line):
		if ";" not in line:
			return line
		stringLine = line.strip().startswith('.')
		stringMode = False
		outLine = ""
		for char in line:
			if stringLine and char == '"':
				stringMode = not stringMode
			if not stringMode and char == ';':
				break
			outLine += char
		# if stringLine:
		# 	print(line)
		return outLine.strip()

	def resolveORG(self, line):
		if not line.startswith("#ORG"):
			return line
		else:
			newPos = eval(line.replace("#ORG", "").strip(), {**self.definitions})
			if (newPos < self.position):
				self.die(f"\nX Error resolving #ORG: new position ({newPos}) is less than current ({self.position}), on line {self.lineNumber+1}")
			outLine = "#DATA " + "0x0000 " * (newPos - self.position)
			return outLine

	def resolveMacros(self, line):
		if line.strip() in self.macros.keys():
			# print(self.macros[line.strip()])
			return self.macros[line.strip()]
		else:
			return line

	def replaceChars(self, line):
		if "'" not in line:
			return line
		if line.strip().startswith('.'):
			return line
		i = 0
		while i < len(line) - 1:
			char = line[i]
			if char == "'":
				if len(line) < i + 2:
					self.die(f"\nX Error resolving char: not enough room, on line {self.lineNumber+1}")
				target = line[i + 1]
				if line[i + 2] != "'":
					self.die(f"\nX Error resolving char '{line[i] + target + line[i + 2] }': no closing apostraphe, on line {self.lineNumber+1}")
				target = self.intToHexString(ord(target))
				line = line[:i] + target + line[i + 3:]
			i += 1
		return line

	def resolveData(self, line):
		if line.strip() == "" or "." not in line:
			return line
		prefix = ""
		if ":" in line and line.strip()[0] != '.':
			prefix = line.split(":")[0] + ": "
			line = ":".join(line.split(':')[1:]).strip()
		if line.strip()[0] == '.':
			dataTypeWord = line.split(" ")[0].strip()
			dataType = {".db": "Byte", ".ds": "String", ".dz": "Zeroes"}.get(dataTypeWord, None)
			if dataType is None:
				self.die(f"\nX Error resolving data type of '{dataTypeWord}' on line {self.lineNumber+1}")
			val = "".join(line.split(" ")[1:])
			if dataType == "Byte":
				try:
					line = self.intToHexString(eval(val, {**self.definitions}))
				except NameError as e:
					self.die(f"\nX Could not resolve name '{e.name}' on line {self.lineNumber+1}")
			if dataType == "String":
				line = self.parseString(line[3:].strip())
			if dataType == "Zeroes":
				try:
					line = "0x0000 " * eval(val, {**self.definitions})
				except NameError as e:
					self.die(f"\nX Could not resolve name '{e.name}' on line {self.lineNumber+1}")
			line = "#DATA " + line
		return prefix + line

	def resolveIncludes(self, line):
		if not line.startswith("#INC"):
			return line
		fileName = line[4:].strip()
		try:
			with open(fileName, 'r') as f:
				loadedContents = f.read()
		except OSError:
			self.die(f"X Error including {fileName}: file not found on line {self.lineNumber+1}")
		if fileName.endswith(".hex"):
			line = " ".join(loadedContents.split())
			for word in line.split(' '):
				if not self.isValidFinalHex(word):
					self.die(f"X Error including {fileName}: token not valid hex '{word}' on line {self.lineNumber+1}")

		elif fileName.endswith(".ghasm"):
			print(f"- Subassembling {fileName}, org is {self.position} on line {self.lineNumber+1}")
			subAssembler = assembler()
			subAssembler.loadFile(fileName)
			line = " ".join(subAssembler.assemble(org=self.position, warnHLT=-1, nested=self.nested+1, definitions=self.definitions).split())
			for k,v in subAssembler.getShared().items():
				if k in self.definitions and v != self.definitions[k]:
					die(f"\nX Subassembled program {fileName} changed definition {k} from {self.definitions[k]} to {v}")
			self.definitions = {**self.definitions, **subAssembler.getShared()}
		else:
			self.die(f"X Error including {fileName}: file extension not supported {self.lineNumber+1}")
		return "#DATA " + line

	def prettyOrList(self, listOfWords): 
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
				if wordNum == len(listOfWords) - 1:
					outString += ("or " + word)
					break
				outString += (word + ", ")
			return outString


	def argumentTypes(self, line):
		if ':' in line:
			line = " ".join(line.split(':')[1:])
		if line == "":
			return []
		if line.strip().startswith("#DATA"):
			return ["Value"] * len(line.strip().replace("#DATA", "", 1).split())
		words = line.strip().split(" ")

		types = []
		for word in words:
			if word in list(AssemblerDefs.Instructions.keys()):
				types.append("Instruction")
			elif word.startswith('$'):
				types.append("Address")
			elif word in ["R0", "R1", "R2", "R3"]:
				types.append("Register")
			elif word != "":
				types.append("Value")
		return types

	def resolveShorthand(self, line):
		words = line.strip().split(" ")
		if words[0] in AssemblerDefs.Shorthand.keys():
			ArgumentTypes = self.argumentTypes(" ".join(words[1:]))
			ArgumentTypesString = "None" if ArgumentTypes == [] else " ".join(ArgumentTypes)
			if ArgumentTypesString in AssemblerDefs.Shorthand[words[0]].keys():
				words[0] = AssemblerDefs.Shorthand[words[0]][ArgumentTypesString]
				return " ".join(words)
			else:
				print(f"\nX Error resolving shorthand command '{words[0]}' with arguments [{', '.join(ArgumentTypes)}], on line {self.lineNumber+1}")
				listOfShorthandArguments = list(AssemblerDefs.Shorthand[words[0]].keys())
				self.die(f"Expected types are: {self.prettyOrList(['[' + ', '.join(typeList.split(' ')) + ']' for typeList in listOfShorthandArguments])}")
		return line

	def validateArguments(self, line):
		words = line.strip().split(" ")
		# Exceptions, should not be instructions
		if line.strip() == '':        # Empty
			return line
		# if ':' in line:               # Label
		# 	return line
		if line.startswith("#DATA"):  # Data
			return line
		# Validating
		if words[0] in AssemblerDefs.Instructions.keys():
			ArgumentTypes = self.argumentTypes(" ".join(words[1:]))
			ArgumentTypesString = "None" if ArgumentTypes == [] else " ".join(ArgumentTypes)
			if not ArgumentTypesString == AssemblerDefs.Instructions[words[0]]['Arguments']:
				print(f"\nX Error validating command '{words[0]}' with arguments [{', '.join(ArgumentTypes)}]")
				expectedArguments = AssemblerDefs.Instructions[words[0]]['Arguments']
				self.die(f"Expected types are: [{', '.join(expectedArguments.split(' '))}]")
		else:
			self.die(f"\nX Error resolving command '{words[0]}'")


	def recordDefs(self, line):
		if line.startswith("#DEF"):
			words = line.split()
			if words[1] in self.definitions.keys():
				self.die(f"X Error recording definitions: the definitions '{line.split(':')[0]}' was encountered earlier at position {self.definitions[line.split(':')[0]]}")
			self.definitions[words[1]] = int(words[2], 0)
			# self.definitions[words[1]] = eval(words[2], {**self.definitions})
			return ""
		return line

	def recordShares(self, line):
		if line.startswith("#SHARE"):
			words = line.split()
			if words[1] == "*":
				self.shareall = True
			else:
				self.shares.append(words[1])
			return ""
		return line

	def getShared(self):
		if self.shareall:
			return self.definitions
		outDict = {}
		for share in self.shares:
			outDict[share] = self.definitions[share]
		return outDict

	def recordLabels(self, line):
		if ':' in line:
			if line.split(':')[0] in self.definitions.keys():
				self.die(f"X Error recording definitions: the definitions '{line.split(':')[0]}' was encountered earlier at position {self.definitions[line.split(':')[0]]}")
			self.definitions[line.split(':')[0]] = self.position
			return ':'.join(line.split(':')[1:]).strip()
		return line

	def isValidFinalHex(self, hexString):
		if len(hexString) != 6:
			return False
		if not hexString.startswith("0x"):
			return False
		if not all(character in '0123456789abcdef' for character in hexString[2:]):
			return False
		# for character in hexString[2:]:
		# 	if character not in '0123456789abcdef':
		# 		return False
		return True

	def intToHexString(self, num):
		if num > 0xffff:
			print(f"! Found the value {str(hex(num))}, which is greater than 0xffff. Rolling to {'0x' + ('0000' + str(hex(num))[2:])[-4:]}")
		return "0x" + (("0" * 4) + str(hex(num))[2:])[-4:]

	def parseString(self, line):
		if line[0] != '"':
			self.die(f"\nX Error parsing string, expected \" to open the string but got {line[0]} on line {self.lineNumber+1}")

		if line[-1] != '"':
			self.die(f"\nX Error parsing string, expected \" to close the string but got {line[-1]} on line {self.lineNumber+1}")

		line = " ".join(self.intToHexString(ord(char)) for char in line[1:-1])
		return line
	
	def assemble(self, org=0, warnHLT=1, nested=0, definitions={}):
		self.definitions = definitions
		self.position = org
		self.nested = nested
		# print(f"Assembling {self.fileName.split('/')[-1]}")
		if "HLT" not in self.fileContents and warnHLT == 1:
			print("! No 'HLT' instruction found: may result in unpredictable behavior")
		elif "HLT" in self.fileContents and warnHLT == -1:
			print("! A 'HLT' instruction found and one is not recommended: may result in unpredictable behavior")
		linesList = self.fileContents.split("\n")
		
		# print("\t" * self.nested + "- Pass 0: Macros!")
		currentMacro = None
		collectedMacroLines = ""
		for lineN, line in enumerate(linesList):
			if currentMacro == None:
				if line.startswith("#MACRO"):
					currentMacro = line.replace("#MACRO", "").strip()
					linesList[lineN] = ""
			else:
				if line == "#ENDM":
					self.macros[currentMacro] = collectedMacroLines.strip()
					currentMacro = None
					collectedMacroLines  = ""
				else:
					collectedMacroLines += line + "\n"
				linesList[lineN] = ""
		if currentMacro != None:
			self.die(f"\nX Error reading macros: EOF while reading macro (did you forget a '#ENDM'?)")




		# print("\t" * self.nested + "- Pass 1: Remove Comments, Replace Chars, Resolve Data, Record labels, Record Defs, Resolve Shorthand, Check Syntax")
		for lineN, line in enumerate(linesList):
			if line == "":
				continue
			# print("-L", line)
			self.lineNumber = lineN
			line = line.strip()
			line = self.clearComments(line)
			line = self.resolveORG(line)
			line = self.resolveMacros(line)
			line = self.recordLabels(line)
			line = self.recordDefs(line)
			line = self.recordShares(line)
			subLinesList = line.split("\n")
			for subLineN, subLine in enumerate(subLinesList):
				# print("-SL", subLine)
				subLine = self.replaceChars(subLine)
				subLine = self.resolveData(subLine)
				subLine = self.resolveIncludes(subLine)
				subLine = self.resolveShorthand(subLine)
				self.validateArguments(subLine)
				# print("+SL", subLine)

				subLinesList[subLineN] = subLine
				# print(self.argumentTypes(line))
			line = "\n".join(subLinesList)

			self.position += sum([self.TypeLengths[typeOfItem] for typeOfItem in self.argumentTypes(line)])

			# print("+L", line)
			linesList[lineN] = line

		# for k, v in self.definitions.items():
		# 	print("\t" * self.nested + "-", "(D)", k, hex(v))

		for k in self.shares:
			print("\t" * self.nested + "-", "(S)", k)

		# print("\t" * self.nested + "- Pass 2: Resolve Labels, Resolving Defs, Resolve Registers, Do Math, Force hexadecimal")

		linesList = "\n".join(linesList).split("\n") # Unfold all the lines that are single list items seperated by "\n" characters from the macro process

		for lineN, line in enumerate(linesList):
			self.lineNumber = lineN
			if line.strip() == "":
				continue
				
			for definition in self.definitions.keys():
				if definition in line:
					pat = r"(\s\$?)(" + definition + r")(?=[\s+\-\/*]|$)"
					line = re.sub(pat, r"\g<1>" + str(self.intToHexString(self.definitions[definition])), line)

			if line.startswith("#DATA"):
				line = line[5:]
			words = line.split(" ")
			for wordNumber, word in enumerate(words):
				if word in ["R0", "R1", "R2", "R3"]:
					words[wordNumber] = ""
					line = " ".join([x for x in words if x != ""])
					continue
				word = word.replace("$", "")
				if word.strip() == "":
					continue
				if any([(op in word) for op in "-+/*"]):
					try:
						word = self.intToHexString(eval(word, {**self.definitions}))
					except NameError as e:
						# self.die(f"\nX Could not resolve name '{e.name}' on line {self.lineNumber+1}") # lineNumber can no longer be trusted after macro'd lines are unfolded
						self.die(f"\nX Could not resolve name '{e.name}'")

				if word in list(AssemblerDefs.Instructions.keys()):
					Binary = AssemblerDefs.Instructions[word]["Binary"]
					if "RR" in Binary:
						Binary = Binary.replace("RR", str(bin(["R0", "R1", "R2", "R3"].index(words[wordNumber + 1])))[2:].zfill(2))
					word = self.intToHexString(int(Binary, 2))

				if not self.isValidFinalHex(word):
					try:
						newWord = self.intToHexString(int(word, 0))
						# print(f"! Assumed token '{word}' to '{newWord}'")
						word = newWord
					except ValueError:
						# self.die(f"\nX Error resolving token '{word}' on line {self.lineNumber+1}, word {wordNumber+1}") # lineNumber can no longer be trusted after macro'd lines are unfolded
						self.die(f"\nX Error resolving token '{word}'")


				words[wordNumber] = word.strip()
				line = " ".join([x for x in words if x != ""])

			

			linesList[self.lineNumber] = line
		# print(f"Assembled {self.fileName.split('/')[-1]}")
		return "\n".join(linesList)  # self.fileContents


if __name__ == '__main__':
	args = sys.argv[1:]
	if len(args) == 0:
		print("Must give a file to build")
	else:
		fileName = args[0]
		x = assembler()
		x.loadFile(fileName)
		fileName = ".".join(fileName.split(".")[:-1]) + ".hex"
		with open(fileName, "w+") as f:
			f.write(x.assemble())
		print(f"Writing to {fileName.split('/')[-1]}")
