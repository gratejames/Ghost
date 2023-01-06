import numpy as np
import os
import sys
import json
from collections import deque
import traceback
import random
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
pygame.init()
AnonFont = pygame.font.Font('./Anonymous_Pro_B.ttf', 20)
AnonFontSmall = pygame.font.Font('./Anonymous_Pro_B.ttf', 11)

from instructionSet import instructionSet 

pallette = {
	"ON":		(0, 255, 0),
	"OFF":		(255, 0, 0),
	"DISABLED":	(100, 0, 0),
}

SpeedMode = True # Turns off ALL debugging for speed (Except for errors and user triggered logs)

DispSet = {
	"point0": 0xa000,
	"dispPos": (295,20),
	"scaler": 3,
}

def badDefinitions(message):
	print(f"badDefinitions: {message}")

def addTuples(t1, t2):
	return (t1[0]+t2[0], t1[1]+t2[1])

def twosComp(val, bits=8): # https://stackoverflow.com/questions/1604464/twos-complement-in-python
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def bitNOT(num):
	return int(str(bin(int(~np.uint8(num))))[4:],2)

# rrrrr gggggg bbbbb
def binColor(num):
	binStr = str(bin(num))[2:].zfill(16)
	return (int(binStr[:5],2) * (255/31),int(binStr[5:11],2) * (255/63),int(binStr[11:16],2) * (255/31))

def Lmap(v, a1,b1,a2,b2):
	return int(a2 + (b2-a2)*((v-a1)/(b1-a1)))



def writeDisplayAddress(addr):
	color = binColor(MEMORY.get(addr, 0))

	relativeAddress = addr - DispSet["point0"]
	x, y = relativeAddress%128, relativeAddress//128

	pixelX, pixelY = ((x*DispSet["scaler"])+DispSet["dispPos"][0], (y*DispSet["scaler"])+DispSet["dispPos"][1])
	pygame.draw.rect(screen, color, (pixelX, pixelY, DispSet["scaler"], DispSet["scaler"]))

	pygame.display.update((pixelX, pixelY), (DispSet["scaler"],DispSet["scaler"]))

def clearDisplay():
	color = (0,0,0)
	for x,y in [(_i,_ii) for _i in range(128) for _ii in range(128)]:
		MEMORY[DispSet["point0"] + x + (y*128)] = 0
	pygame.draw.rect(screen, color, (DispSet["dispPos"][0], DispSet["dispPos"][1], 128*DispSet["scaler"], 128*DispSet["scaler"]))
	pygame.display.update(pygame.Rect(DispSet["dispPos"], (128*DispSet["scaler"], 128*DispSet["scaler"])))

def refreshDisplay():
	for x,y in [(_i,_ii) for _i in range(128) for _ii in range(128)]:
		color = binColor(MEMORY.get(DispSet["point0"] + x + (y*128), 0))
		pixelX, pixelY = ((x*DispSet["scaler"])+DispSet["dispPos"][0], (y*DispSet["scaler"])+DispSet["dispPos"][1])
		pygame.draw.rect(screen, color, (pixelX, pixelY, DispSet["scaler"], DispSet["scaler"]))
	pygame.display.update(pygame.Rect(DispSet["dispPos"], (128*DispSet["scaler"], 128*DispSet["scaler"])))

def updateStackGUI():
	stack1Size = MEMORY.get(0xe000, 0)
	pygame.draw.rect(screen, pallette["OFF"], pygame.Rect(110,35,80,10))
	pygame.draw.rect(screen, pallette["ON"],  pygame.Rect(110,37,Lmap(stack1Size, 0, 4096, 0, 80),8))

	stack2Size = MEMORY.get(0xf000, 0)
	pygame.draw.rect(screen, pallette["OFF"], pygame.Rect(110,50,80,10))
	pygame.draw.rect(screen, pallette["ON"],  pygame.Rect(110,50,Lmap(stack2Size, 0, 4096, 0, 80),8))

	pygame.display.update((110,35), (190,60))

def updateGUI():
	pygame.draw.rect(screen, pallette["DISABLED"] if (Halted or Break) else pallette["ON"] if PowerSwitch["state"] else pallette["OFF"], PowerSwitch["rect"])
	textSurface = AnonFontSmall.render("POW", False, (0, 0, 0))
	screen.blit(textSurface, (PowerSwitch["rect"].x+1, PowerSwitch["rect"].y+13))

	pygame.draw.rect(screen, pallette["DISABLED"] if Halted else pallette["ON"] if ClockButton["state"] else pallette["OFF"], ClockButton["rect"])
	textSurface = AnonFontSmall.render("CLK", False, (0, 0, 0))
	screen.blit(textSurface, (ClockButton["rect"].x+2, ClockButton["rect"].y+13))

	pygame.draw.rect(screen, pallette["ON"] if ResetButton["state"] else pallette["OFF"], ResetButton["rect"])
	textSurface = AnonFontSmall.render("RST", False, (0, 0, 0))
	screen.blit(textSurface, (ResetButton["rect"].x+2, ResetButton["rect"].y+13))
	# Stack Status'
	textSurface = AnonFontSmall.render("Stack status", False, (0, 0, 0))
	screen.blit(textSurface, (110,20))
	stack1Size = MEMORY.get(0xe000, 0)
	pygame.draw.rect(screen, pallette["OFF"], pygame.Rect(110,35,80,10))
	pygame.draw.rect(screen, pallette["ON"],  pygame.Rect(110,37,Lmap(stack1Size, 0, 4096, 0, 80),8))

	stack2Size = MEMORY.get(0xf000, 0)
	pygame.draw.rect(screen, pallette["OFF"], pygame.Rect(110,50,80,10))
	pygame.draw.rect(screen, pallette["ON"],  pygame.Rect(110,50,Lmap(stack2Size, 0, 4096, 0, 80),8))

	pygame.display.update((20,20), (170,40))


screen = pygame.display.set_mode((700, 500), pygame.RESIZABLE)
pygame.display.set_caption('Ghost Computer Simulator | By Jimmy')

timingMode = False

Halted = False
Break = False
done = False
clock = pygame.time.Clock()
CycleClock = 0 # Used to pass space button press between weird contexts

args = sys.argv[1:]
if len(args) == 0:
	fileName = "main.hex"
else:
	fileName = args[0]

with open(fileName, 'r') as f:
	MEMORY = {}
	for counter, word in enumerate(f.read().split()):
		word = word.strip()
		if word == "":
			continue
		MEMORY[counter] = int(word, 16)

MEMORY[0xe000] = 0
MEMORY[0xf000] = 0

PC           = 0 	# Program Counter
AddrRegister = 0 	# Address register
Registers = [
	0,				# Register0
	0,				# Register1
	0,				# Register2
	0,				# Register3
]
JumpRegister = False

PowerSwitch = {
	"rect": pygame.Rect(20,20,20,40),
	"state": timingMode,
}
ClockButton = {
	"rect": pygame.Rect(50,20,20,40),
	"state": False,
	"prevState": False,
}
ResetButton = {
	"rect": pygame.Rect(80,20,20,40),
	"state": False,
}

screen.fill((50, 50, 50))
pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(10, 10, screen.get_width()-20, screen.get_height()-20))
clearDisplay()
updateGUI()
pygame.display.flip()

def ForceValidInt(x):
	while x < 0:
		x += 0xffff
	return x%0x10000

def GetVal():
	global PC
	PC += 1
	return MEMORY[PC]
def GetAddress():
	global PC
	PC += 1
	addr = MEMORY[PC]
	if addr == 0x9fff: # Random number generator
		rand = random.randrange(0xffff)
		return rand
	return MEMORY.get(addr, 0)
def SetAddress(val):
	global PC
	PC += 1
	WriteMem(MEMORY[PC], val)
def WriteMem(addr, val):
	MEMORY[addr] = ForceValidInt(val)
	if addr >= 0xa000 and addr <= 0xdfff:
		writeDisplayAddress(addr)

def go():
	global done, Halted, Break, PC, Registers, AddrRegister, ClockButton, PowerSwitch, ResetButton, CycleClock, JumpRegister
	t=0
	while not done:
		ClockButton["prevState"] = ClockButton["state"]
		if Halted or Break:
			PowerSwitch["state"] = False
		t+=1
		nextInput = 0
		if t%20==0:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					done = True
				elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
					if event.button == 1:
						newClick = event.pos
						if PowerSwitch["rect"].collidepoint(newClick) and event.type == pygame.MOUSEBUTTONDOWN:
							PowerSwitch["state"] = not PowerSwitch["state"]
						if ClockButton["rect"].collidepoint(newClick):
							ClockButton["state"] = (event.type == pygame.MOUSEBUTTONDOWN)
							if not ClockButton["state"]:
								Break = False
						if ResetButton["rect"].collidepoint(newClick):
							ResetButton["state"] = (event.type == pygame.MOUSEBUTTONDOWN)
						updateGUI()
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_UP:
						MEMORY[0x9f00] = 0
					if event.key == pygame.K_DOWN:
						MEMORY[0x9f01] = 0
					if event.key == pygame.K_LEFT:
						MEMORY[0x9f02] = 0
					if event.key == pygame.K_RIGHT:
						MEMORY[0x9f03] = 0
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						MEMORY[0x9f00] = 1
					if event.key == pygame.K_DOWN:
						MEMORY[0x9f01] = 1
					if event.key == pygame.K_LEFT:
						MEMORY[0x9f02] = 1
					if event.key == pygame.K_RIGHT:
						MEMORY[0x9f03] = 1
					if event.key == pygame.K_SLASH:
						os.system('clear')
						print("DUMP:")
						print("    PC:  ", PC, "\t(0x"+str(hex(PC))[2:].zfill(4)+")")
						print("    R0:  ", Registers[0], "\t(0x"+str(hex(Registers[0]))[2:].zfill(4)+")")
						print("    R1:  ", Registers[1], "\t(0x"+str(hex(Registers[1]))[2:].zfill(4)+")")
						print("    R2:  ", Registers[2], "\t(0x"+str(hex(Registers[2]))[2:].zfill(4)+")")
						print("    R3:  ", Registers[3], "\t(0x"+str(hex(Registers[3]))[2:].zfill(4)+")")
						print("    Addr:", AddrRegister, "\t(0x"+str(hex(AddrRegister))[2:].zfill(4)+")")
						print("    SP1: ", MEMORY[0xe000], "\t(0x"+str(hex(MEMORY[0xe000]))[2:].zfill(4)+")")
						print("    SP2: ", MEMORY[0xf000], "\t(0x"+str(hex(MEMORY[0xf000]))[2:].zfill(4)+")")
						print("    JMP: ", JumpRegister)
						print("    Memory:")
						for add, val in MEMORY.items():
							if add > 0x9eff:
								continue
							suffix = f'< {instructionSet[str((val//4)*4)+"RR" if str((val//4)*4)+"RR" in instructionSet.keys() else str(val)]}' if add == PC else ""
							print("       ", "0x"+str(hex(add))[2:].zfill(4)+":", val, "\t(0x"+str(hex(val))[2:].zfill(4)+")", suffix)
					if event.key == pygame.K_s:
						os.system('clear')
						print("Stack 1:")
						for add, val in MEMORY.items():
							if add >= 0xefff:
								continue
							if (add >= 0xe000) or add == 0xe000:
								print("    ", "0x"+str(hex(add))[2:].zfill(4)+":", val, "\t(0x"+str(hex(val))[2:].zfill(4)+")")
					if event.key == pygame.K_d:
						os.system('clear')
						print("Stack 1:")
						for add, val in MEMORY.items():
							if add >= 0xffff:
								continue
							if (add >= 0xf000) or add == 0xf000:
								print("    ", "0x"+str(hex(add))[2:].zfill(4)+":", val, "\t(0x"+str(hex(val))[2:].zfill(4)+")")
					if event.key == pygame.K_SPACE:
						CycleClock = 1
					if event.key == pygame.K_1:
						CycleClock = 10
					if event.key == pygame.K_2:
						CycleClock = 100
					if event.key == pygame.K_3:
						CycleClock = 1000


		if ResetButton["state"]:
			clearDisplay()
			PC           = 0 	# Program Counter
			AddrRegister = 0 	# Address register
			Registers = [
				0,				# Register0
				0,				# Register1
				0,				# Register2
				0,				# Register3
			]
			MEMORY[0xe000] = 0
			MEMORY[0xf000] = 0
			JumpRegister = False
			Halted = False
			Break = False
			CycleClock = 0

		if Halted and timingMode:
			done = True

		if Halted or Break:
			updateGUI()
			CycleClock = 0

		if (PowerSwitch["state"] or (ClockButton["state"] == True and ClockButton["prevState"] == False) or (CycleClock > 0)) and not Halted and not Break:
			if CycleClock > 0:
				CycleClock -= 1

			instruction = MEMORY.get(PC, 0)
			instructionString = instructionSet[str((instruction//4)*4)+"RR" if str((instruction//4)*4)+"RR" in instructionSet.keys() else str(instruction)]

			if instructionString == "NOP":
				pass
			elif instructionString == "STV":
				val = GetVal()
				SetAddress(val)
			elif instructionString == "MVA":
				SetAddress(GetAddress())
			elif instructionString == "LDA":
				Registers[instruction%4] = GetAddress()
			elif instructionString == "LDV":
				Registers[instruction%4] = GetVal()
			elif instructionString == "STR":
				SetAddress(Registers[instruction%4])
			elif instructionString == "ADA":
				Registers[instruction%4] += GetAddress()
			elif instructionString == "ADV":
				Registers[instruction%4] += GetVal()
			elif instructionString == "SBA":
				Registers[instruction%4] += -GetAddress()
			elif instructionString == "SBV":
				Registers[instruction%4] += -GetVal()
			elif instructionString == "SRA":
				Registers[instruction%4] = GetAddress() - Registers[instruction%4]
			elif instructionString == "SRV":
				Registers[instruction%4] = GetVal() - Registers[instruction%4]
			elif instructionString == "NEG":
				Registers[instruction%4] = twosComp(Registers[instruction%4])
			elif instructionString == "INC":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] + 1)
			elif instructionString == "DEC":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] - 1)
			elif instructionString == "SHL1":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] << 1)
			elif instructionString == "SHR1":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] >> 1)
			elif instructionString == "ANA":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] & GetAddress())
			elif instructionString == "ANV":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] & GetVal())
			elif instructionString == "NNA":
				Registers[instruction%4] = ForceValidInt(bitNOT(Registers[instruction%4] & GetAddress()))
			elif instructionString == "NNV":
				Registers[instruction%4] = ForceValidInt(bitNOT(Registers[instruction%4] & GetVal()))
			elif instructionString == "ORA":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] | GetAddress())
			elif instructionString == "ORV":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] | GetVal())
			elif instructionString == "XRA":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] ^ GetAddress())
			elif instructionString == "XRV":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] ^ GetVal())
			elif instructionString == "NOT":
				Registers[instruction%4] = ForceValidInt(bitNOT(Registers[instruction%4]))
			elif instructionString == "DDR":
				AddrRegister = Registers[instruction%4]
			elif instructionString == "DDA":
				AddrRegister = GetAddress()
			elif instructionString == "DDV":
				AddrRegister = GetVal()
			elif instructionString == "JPA":
				PC = GetVal()-1
			elif instructionString == "JPD":
				PC = AddrRegister-1
			elif instructionString == "CZR":
				JumpRegister = Registers[instruction%4]==0
			elif instructionString == "CEA":
				JumpRegister = Registers[instruction%4]==GetAddress()
			elif instructionString == "CEV":
				JumpRegister = Registers[instruction%4]==GetVal()
			elif instructionString == "CLA":
				JumpRegister = Registers[instruction%4]<GetAddress()
			elif instructionString == "CLV":
				JumpRegister = Registers[instruction%4]<GetVal()
			elif instructionString == "CGA":
				JumpRegister = Registers[instruction%4]>GetAddress()
			elif instructionString == "CGV":
				JumpRegister = Registers[instruction%4]>GetVal()
			elif instructionString == "CALD":
				StackPointer = MEMORY[0xe000] = MEMORY[0xe000] + 1 # Update stack pointer
				MEMORY[0xe000 + StackPointer] = PC+1 # Put current PC in stack
				PC = AddrRegister-1 # Update PC to Address
				# updateStackGUI()
			elif instructionString == "CALA":
				StackPointer = MEMORY[0xe000] = MEMORY[0xe000] + 1 # Update stack pointer
				newAddr = GetVal() # Update PC with addr read before writing it to the stack
				MEMORY[0xe000 + StackPointer] = PC+1 # Put current PC in stack
				PC = newAddr-1 # Update PC to Address
				# updateStackGUI()
			elif instructionString == "RT":
				StackPointer = MEMORY[0xe000] # Get stack pointer
				PC = MEMORY[0xe000 + StackPointer]-1 # Load PC from stack
				MEMORY[0xe000] = MEMORY[0xe000] - 1 # Decrease stack
				# updateStackGUI()
			elif instructionString == "PSHL":
				for val in Registers:
					StackPointer = MEMORY[0xf000] = MEMORY[0xf000] + 1 # Update stack pointer
					MEMORY[0xf000 + StackPointer] = val
				# updateStackGUI()
			elif instructionString == "POPL":
				for i in range(len(Registers)-1,-1,-1): # Reverse order - [3, 2, 1, 0]
					StackPointer = MEMORY[0xf000]
					Registers[i] = MEMORY[0xf000 + StackPointer]
					MEMORY[0xf000] = MEMORY[0xf000] - 1 # Update stack pointer
				# updateStackGUI()
			elif instructionString == "RTC":
				if JumpRegister:
					StackPointer = MEMORY[0xe000] # Get stack pointer
					PC = MEMORY[0xe000 + StackPointer]-1 # Load PC from stack
					MEMORY[0xe000] = MEMORY[0xe000] - 1 # Decrease stack
				# updateStackGUI()
			elif instructionString == "PSHR":
				StackPointer = MEMORY[0xf000] = MEMORY[0xf000] + 1 # Update stack pointer
				MEMORY[0xf000 + StackPointer] = Registers[instruction%4]
				# updateStackGUI()
			elif instructionString == "POPR":
				StackPointer = MEMORY[0xf000]
				Registers[instruction%4] = MEMORY[0xf000 + StackPointer]
				MEMORY[0xf000] = MEMORY[0xf000] - 1 # Update stack pointer
				# updateStackGUI()
			elif instructionString == "STRR":
				MEMORY[AddrRegister] = Registers[instruction%4]
				if AddrRegister >= 0xa000 and AddrRegister <= 0xdfff:
					writeDisplayAddress(AddrRegister)
			elif instructionString == "STRV":
				WriteMem(MEMORY[AddrRegister], getValue())
			elif instructionString == "LDRR":
				Registers[instruction%4] = MEMORY[AddrRegister]
			elif instructionString == "SHLV":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] << GetVal())
			elif instructionString == "SHRV":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] >> GetVal())
			elif instructionString == "SHLA":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] << GetAddress())
			elif instructionString == "SHRA":
				Registers[instruction%4] = ForceValidInt(Registers[instruction%4] >> GetAddress())
			elif instructionString == "ADDR":
				Registers[0] = ForceValidInt(Registers[0] + Registers[instruction%4])
			elif instructionString == "SUBR":
				Registers[0] = ForceValidInt(Registers[0] - Registers[instruction%4])
			elif instructionString == "SBRR":
				Registers[0] = ForceValidInt(Registers[instruction%4] - Registers[0])
			elif instructionString == "SHL0":
				Registers[0] = ForceValidInt(Registers[0] << Registers[instruction%4])
			elif instructionString == "SHR0":
				Registers[0] = ForceValidInt(Registers[0] >> Registers[instruction%4])
			elif instructionString == "CZA":
				JumpRegister = GetAddress()==0

			elif instructionString == "CNZR":
				JumpRegister = Registers[instruction%4]!=0
			elif instructionString == "CZA":
				JumpRegister = GetAddress()==0
			elif instructionString == "CNZA":
				JumpRegister = GetAddress()!=0

			elif instructionString == "JCA":
				newAddr = GetVal()
				if JumpRegister:
					PC = newAddr-1
			elif instructionString == "JCD":
				if JumpRegister:
					PC = AddrRegister-1

			elif instructionString == "CCA":
				newAddr = GetVal() # Update PC with addr read before writing it to the stack
				if JumpRegister:
					StackPointer = MEMORY[0xe000] = MEMORY[0xe000] + 1 # Update stack pointer
					MEMORY[0xe000 + StackPointer] = PC+1 # Put current PC in stack
					PC = newAddr-1 # Update PC to Address
				# updateStackGUI()
			elif instructionString == "CCD":
				if JumpRegister:
					StackPointer = MEMORY[0xe000] = MEMORY[0xe000] + 1 # Update stack pointer
					MEMORY[0xe000 + StackPointer] = PC+1 # Put current PC in stack
					PC = AddrRegister-1 # Update PC to Address
				# updateStackGUI()

			elif instructionString == "CNEA":
				JumpRegister = Registers[instruction%4]!=GetAddress()
			elif instructionString == "CNEV":
				JumpRegister = Registers[instruction%4]!=GetVal()

			elif instructionString == "BRK":
				Break = True
			elif instructionString == "HLT":
				Halted = True
			else:
				print("ERR:", instructionString)
				done = True

			for i in range(len(Registers)):
				Registers[i] = Registers[i]%0x10000

			if not Halted:
				PC += 1
try:
	go()
except:
	print("DUMP:")
	print("    PC:  ", PC, "\t(0x"+str(hex(PC))[2:].zfill(4)+")")
	print("    R0:  ", Registers[0], "\t(0x"+str(hex(Registers[0]))[2:].zfill(4)+")")
	print("    R1:  ", Registers[1], "\t(0x"+str(hex(Registers[1]))[2:].zfill(4)+")")
	print("    R2:  ", Registers[2], "\t(0x"+str(hex(Registers[2]))[2:].zfill(4)+")")
	print("    R3:  ", Registers[3], "\t(0x"+str(hex(Registers[3]))[2:].zfill(4)+")")
	print("    Addr:", AddrRegister, "\t(0x"+str(hex(AddrRegister))[2:].zfill(4)+")")
	print("    SP1: ", MEMORY[0xe000], "\t(0x"+str(hex(MEMORY[0xe000]))[2:].zfill(4)+")")
	print("    SP2: ", MEMORY[0xf000], "\t(0x"+str(hex(MEMORY[0xf000]))[2:].zfill(4)+")")
	print("    JMP: ", JumpRegister)
	print("    Memory:")
	for add, val in MEMORY.items():
		if add > 0x9eff:
			continue
		try:
			suffix = f'< {instructionSet[str((val//4)*4)+"RR" if str((val//4)*4)+"RR" in instructionSet.keys() else str(val)]}' if add == PC else ""
		except KeyError:
			suffix = '< ?'
		print("       ", "0x"+str(hex(add))[2:].zfill(4)+":", val, "\t(0x"+str(hex(val))[2:].zfill(4)+")", suffix)
	traceback.print_exc()
pygame.quit()