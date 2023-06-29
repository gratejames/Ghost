import numpy as np
import os
import sys
import json
from collections import deque
import traceback
import ctypes
import random
import timeit
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import instructionSet as instrSet
import configparser
from helper import *
pygame.init()

AbsolutePath = os.path.abspath(os.path.dirname(__file__))
FontPath = os.path.join(AbsolutePath, 'Anonymous_Pro_B.ttf')
AnonFont = pygame.font.Font(FontPath, 20)
AnonFontSmall = pygame.font.Font(FontPath, 11)

instructionSet = [0] * 0x100
for k, v in instrSet.instructionSet.items():
	instructionSet[int(k)] = v

class settings:
	def __init__(self, fileName):
		config = configparser.ConfigParser()
		config.read(os.path.join(AbsolutePath, fileName))


		self.TimingMode 		= eval(config["Misc"]["TimingMode"])
		
		self.display 			= self.display(config["Display"])
		self.palette 			= self.palette(config["Palette"])
		self.stack   			= self.stack(config["Stack"])
		
		self.PowerSwitch 		= self.PowerSwitch(config["Display.Power"])
		self.ClockButton 		= self.ClockButton(config["Display.Clock"])
		self.ResetButton 		= self.ResetButton(config["Display.Reset"])


	class PowerSwitch:
		def __init__(self, cfg):
			self.rect 			= pygame.Rect(*eval(cfg["Pos"]), *eval(cfg["Size"]))
			self.textSurface 	= AnonFontSmall.render(cfg["Text"], False, (0, 0, 0))
	class ClockButton:
		def __init__(self, cfg):
			self.rect 			= pygame.Rect(*eval(cfg["Pos"]), *eval(cfg["Size"]))
			self.textSurface 	= AnonFontSmall.render(cfg["Text"], False, (0, 0, 0))
	class ResetButton:
		def __init__(self, cfg):
			self.rect 			= pygame.Rect(*eval(cfg["Pos"]), *eval(cfg["Size"]))
			self.textSurface 	= AnonFontSmall.render(cfg["Text"], False, (0, 0, 0))
	class display:
		def __init__(self, cfg):
			self.bg				= eval(cfg["BackgroundColor"])
			self.address		= int(cfg["Address"], 0)
			self.position		= eval(cfg["Position"])
			self.scale			= int(cfg["Scale"])
			
	class palette:
		def __init__(self, cfg):
			self.ON				= eval(cfg["ON"])
			self.OFF			= eval(cfg["OFF"])
			self.DISABLED		= eval(cfg["DISABLED"])
	class stack:
		def __init__(self, cfg):
			self.refresh		= int(cfg["Refresh"])
			
			pos1 = eval(cfg["1Pos"])
			pos2 = eval(cfg["2Pos"])
			size = eval(cfg["Size"])
			reveal = int(cfg["Reveal"])
			self.s1.rect		= pygame.Rect(*pos1, *size)
			self.s1.pos			= pos1
			self.s1.width		= size[0] - reveal
			self.s1.address		= int(cfg["1Address"], 0)
			self.s2.rect		= pygame.Rect(*pos2, *size)
			self.s2.pos			= pos2
			self.s2.width		= size[0] - reveal
			self.s2.address		= int(cfg["2Address"], 0)
		class s1:
			pass
		class s2:
			pass

settings = settings("settings.ini")

class state:
	Done 			= False
	
	Halted 			= False
	Break 			= False
	CycleClock 		= 0 # Used to pass space button press between weird contexts

	PowerSwitch     = settings.TimingMode
	ResetButton     = False
	ClockButton     = False
	ClockButtonPrev = False
		
	def Reset(self):
		self.Halted			= False
		self.Break			= False
		self.CycleClock		= 0
		
		self.PowerSwitch	= False


state = state()

def writeDisplayAddress(addr):
	color = binColor(MEMORY[addr])

	relativeAddress = addr - settings.display.address
	x, y = relativeAddress%128, relativeAddress//128

	pixelX, pixelY = ((x*settings.display.scale)+settings.display.position[0], (y*settings.display.scale)+settings.display.position[1])
	pygame.draw.rect(screen, color, (pixelX, pixelY, settings.display.scale, settings.display.scale))

	pygame.display.update((pixelX, pixelY), (settings.display.scale,settings.display.scale))
	
	# print(1, timeit.timeit(lambda:pygame.display.update((pixelX, pixelY), (settings.display.scale,settings.display.scale)), number=1000))
	# print(2, timeit.timeit(lambda:pygame.display.update((0, 0), (128,128)), number=1000))
	

def clearDisplay(color = (0,0,0)):
	for x,y in [(_i,_ii) for _i in range(128) for _ii in range(128)]:
		MEMORY[settings.display.address + x + (y*128)] = 0
	pygame.draw.rect(screen, color, (settings.display.position[0], settings.display.position[1], 128*settings.display.scale, 128*settings.display.scale))
	pygame.display.update(pygame.Rect(settings.display.position, (128*settings.display.scale, 128*settings.display.scale)))

def refreshDisplay():
	pygame.display.update(settings.display.position, (128*settings.display.scale, 128*settings.display.scale))




# stack1SizeLast = None
# stack2SizeLast = None
# stackUpdateRect = (settings.stack.s1.pos, (settings.stack.s2.rect.x+settings.stack.s2.rect.width,settings.stack.s2.rect.y+settings.stack.s2.rect.height))
# def updateStackGUI():
# 	pass
# 	stack1Size = Lmap(MEMORY[settings.stack.s1.address], 0, 4096, 0, 80//settings.stack.refresh)
# 	chg1 = stack1SizeLast != stack1Size
# 	if chg1:
# 		pygame.draw.rect(screen, settings.palette.OFF, settings.stack.s1.rect)
# 		pygame.draw.rect(screen, settings.palette.ON,  pygame.Rect(settings.stack.s1.pos,(settings.stack.s1.width,stack1Size*settings.stack.refresh)))

# 	stack2Size = Lmap(MEMORY[settings.stack.s2.address], 0, 4096, 0, 80//settings.stack.refresh)
# 	chg2 = stack2SizeLast != stack2Size
# 	if chg2:
# 		pygame.draw.rect(screen, settings.palette.OFF, settings.stack.s2.rect)
# 		pygame.draw.rect(screen, settings.palette.ON,  pygame.Rect(settings.stack.s2.pos,(settings.stack.s2.width,stack2Size*settings.stack.refresh)))
	
# 	if chg1 or chg2:
# 		pygame.display.update(stackUpdateRect)

def updateGUI():
	pygame.draw.rect(screen, settings.palette.DISABLED if (state.Halted or state.Break) else settings.palette.ON if state.PowerSwitch else settings.palette.OFF, settings.PowerSwitch.rect)
	screen.blit(settings.PowerSwitch.textSurface, (settings.PowerSwitch.rect.x+1, settings.PowerSwitch.rect.y+6))

	pygame.draw.rect(screen, settings.palette.DISABLED if state.Halted else settings.palette.ON if state.ClockButton else settings.palette.OFF, settings.ClockButton.rect)
	screen.blit(settings.ClockButton.textSurface, (settings.ClockButton.rect.x+2, settings.ClockButton.rect.y+6))

	pygame.draw.rect(screen, settings.palette.ON if state.ResetButton else settings.palette.OFF, settings.ResetButton.rect)
	screen.blit(settings.ResetButton.textSurface, (settings.ResetButton.rect.x+2, settings.ResetButton.rect.y+6))
	
	pygame.display.update((10,10), (30,90))

	# updateStackGUI()



pygame.display.set_caption('Ghost Computer Simulator | By Jimmy')
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
screen = pygame.display.set_mode((128*settings.display.scale+50, 128*settings.display.scale+20), pygame.DOUBLEBUF)#, pygame.RESIZABLE)
screen.set_alpha(None)

clock = pygame.time.Clock()

args = sys.argv[1:]
if len(args) == 0:
	fileName = "main.hex"
else:
	fileName = args[0]

with open(fileName, 'r') as f:
	MEMORY = (ctypes.c_ushort * 0xffff)()
	for counter, word in enumerate(f.read().split()):
		word = word.strip()
		if word == "":
			continue
		MEMORY[counter] = int(word, 16)

MEMORY[settings.stack.s1.address] = 0
MEMORY[settings.stack.s2.address] = 0

InstructionsProcessed = 0
PC           = 0 	# Program Counter
AddrRegister = 0 	# Address register
Registers = [
	0,				# Register0
	0,				# Register1
	0,				# Register2
	0,				# Register3
]
JumpRegister 	= False

screen.fill(settings.display.bg)
clearDisplay()
updateGUI()
pygame.display.flip()



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
	return MEMORY[addr]
def SetAddress(val):
	global PC
	PC += 1
	WriteMem(MEMORY[PC], val)
	
def WriteMem(addr, val):
	MEMORY[addr] = ForceValidInt(val)
	if addr >= 0xa000 and addr <= 0xdfff:
		writeDisplayAddress(addr)

def eventChecks():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			state.Done = True
		elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
			if event.button == 1:
				newClick = event.pos
				if settings.PowerSwitch.rect.collidepoint(newClick) and event.type == pygame.MOUSEBUTTONDOWN:
					state.PowerSwitch = not state.PowerSwitch
				if settings.ClockButton.rect.collidepoint(newClick):
					state.ClockButton = (event.type == pygame.MOUSEBUTTONDOWN)
					if not state.ClockButton:
						state.Break = False
				if settings.ResetButton.rect.collidepoint(newClick):
					state.ResetButton = (event.type == pygame.MOUSEBUTTONDOWN)
				updateGUI()
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_UP:
				MEMORY[0x9f00] = 0
			elif event.key == pygame.K_DOWN:
				MEMORY[0x9f01] = 0
			elif event.key == pygame.K_LEFT:
				MEMORY[0x9f02] = 0
			elif event.key == pygame.K_RIGHT:
				MEMORY[0x9f03] = 0
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				MEMORY[0x9f00] = 1
			elif event.key == pygame.K_DOWN:
				MEMORY[0x9f01] = 1
			elif event.key == pygame.K_LEFT:
				MEMORY[0x9f02] = 1
			elif event.key == pygame.K_RIGHT:
				MEMORY[0x9f03] = 1
			elif event.key == pygame.K_SLASH:
				os.system('clear')
				print("DUMP:")
				print("    PC:  ", PC, "\t(0x"+str(hex(PC))[2:].zfill(4)+")")
				print("    R0:  ", Registers[0], "\t("+Pretty(Registers[0])+")")
				print("    R1:  ", Registers[1], "\t("+Pretty(Registers[1])+")")
				print("    R2:  ", Registers[2], "\t("+Pretty(Registers[2])+")")
				print("    R3:  ", Registers[3], "\t("+Pretty(Registers[3])+")")
				print("    Addr:", AddrRegister, "\t(" + Pretty(AddrRegister)+")")
				print("    SP1: ", MEMORY[settings.stack.s1.address], "\t("+Pretty(MEMORY[settings.stack.s1.address])+")")
				print("    SP2: ", MEMORY[settings.stack.s2.address], "\t("+Pretty(MEMORY[settings.stack.s2.address])+")")
				print("    JMP: ", JumpRegister)
				# print("    Memory:")
				# for add, val in MEMORY.items():
				# 	if add > 0x9eff:
				# 		continue
				# 	suffix = f'< {instructionSet[str((val//4)*4)+"RR" if str((val//4)*4)+"RR" in instructionSetkeys else str(val)]}' if add == PC else ""
				# 	print("       ", Pretty(add)+":", val, "\t("+Pretty(val), suffix)
			elif event.key == pygame.K_s:
				os.system('clear')
				print("Stack 1:")
				for add, val in enumerate(MEMORY):
					if add >= 0xefff:
						continue
					if (add >= settings.stack.s1.address) or add == settings.stack.s1.address:
						print("    ", Pretty(add)+":", val, "\t("+Pretty(val)+")")
			elif event.key == pygame.K_d:
				os.system('clear')
				print("Stack 1:")
				for add, val in enumerate(MEMORY):
					if add >= 0xffff:
						continue
					if (add >= settings.stack.s2.address) or add == settings.stack.s2.address:
						print("    ", Pretty(add)+":", val, "\t("+Pretty(val)+")")
			elif event.key == pygame.K_SPACE:
				state.CycleClock = 1
			elif event.key == pygame.K_1:
				state.CycleClock = 10
			elif event.key == pygame.K_2:
				state.CycleClock = 100
			elif event.key == pygame.K_3:
				state.CycleClock = 1000
				
def executeInstruction(instruction):
	global state, PC, Registers, AddrRegister, JumpRegister
	# print(instruction, hex(instruction))
	instructionString = instructionSet[instruction]
	# with open("Instructions.log", 'a+') as f:
	# 	f.write(str(instruction) + "\n")
		# f.write(str(instruction) + " instruction: " + instructionString + "\n")
	match instructionString:
		case "NOP":
			pass
		case "STV":
			val = GetVal()
			SetAddress(val)
		case "SCR":
			refreshDisplay()
		case "MVA":
			SetAddress(GetAddress())
		case "LDA":
			Registers[instruction%4] = GetAddress()
		case "LDV":
			Registers[instruction%4] = GetVal()
		case "STR":
			SetAddress(Registers[instruction%4])
		case "ADA":
			Registers[instruction%4] += GetAddress()
		case "ADV":
			Registers[instruction%4] += GetVal()
		case "SBA":
			Registers[instruction%4] += -GetAddress()
		case "SBV":
			Registers[instruction%4] += -GetVal()
		case "SRA":
			Registers[instruction%4] = GetAddress() - Registers[instruction%4]
		case "SRV":
			Registers[instruction%4] = GetVal() - Registers[instruction%4]
		case "NEG":
			Registers[instruction%4] = twosComp(Registers[instruction%4])
		case "INC":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] + 1)
		case "DEC":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] - 1)
		case "SHL1":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] << 1)
		case "SHR1":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] >> 1)
		case "ANA":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] & GetAddress())
		case "ANV":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] & GetVal())
		case "NNA":
			Registers[instruction%4] = ForceValidInt(bitNOT(Registers[instruction%4] & GetAddress()))
		case "NNV":
			Registers[instruction%4] = ForceValidInt(bitNOT(Registers[instruction%4] & GetVal()))
		case "ORA":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] | GetAddress())
		case "ORV":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] | GetVal())
		case "XRA":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] ^ GetAddress())
		case "XRV":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] ^ GetVal())
		case "NOT":
			Registers[instruction%4] = ForceValidInt(bitNOT(Registers[instruction%4]))
		case "DDR":
			AddrRegister = Registers[instruction%4]
		case "DDA":
			AddrRegister = GetAddress()
		case "DDV":
			AddrRegister = GetVal()
		case "JPA":
			PC = GetVal()-1
		case "JPD":
			PC = AddrRegister-1
		case "CZR":
			JumpRegister = Registers[instruction%4]==0
		case "CEA":
			JumpRegister = Registers[instruction%4]==GetAddress()
		case "CEV":
			JumpRegister = Registers[instruction%4]==GetVal()
		case "CLA":
			JumpRegister = Registers[instruction%4]<GetAddress()
		case "CLV":
			JumpRegister = Registers[instruction%4]<GetVal()
		case "CGA":
			JumpRegister = Registers[instruction%4]>GetAddress()
		case "CGV":
			JumpRegister = Registers[instruction%4]>GetVal()
		case "CALD":
			StackPointer = MEMORY[settings.stack.s1.address] = MEMORY[settings.stack.s1.address] + 1 # Update stack pointer
			MEMORY[settings.stack.s1.address + StackPointer] = PC+1 # Put current PC in stack
			PC = AddrRegister-1 # Update PC to Address
			# updateStackGUI()
		case "CALA":
			StackPointer = MEMORY[settings.stack.s1.address] = MEMORY[settings.stack.s1.address] + 1 # Update stack pointer
			newAddr = GetVal() # Update PC with addr read before writing it to the stack
			MEMORY[settings.stack.s1.address + StackPointer] = PC+1 # Put current PC in stack
			PC = newAddr-1 # Update PC to Address
			# updateStackGUI()
		case "RT":
			StackPointer = MEMORY[settings.stack.s1.address] # Get stack pointer
			PC = MEMORY[settings.stack.s1.address + StackPointer]-1 # Load PC from stack
			MEMORY[settings.stack.s1.address] = MEMORY[settings.stack.s1.address] - 1 # Decrease stack
			# updateStackGUI()
		case "PSHL":
			for val in Registers:
				StackPointer = MEMORY[settings.stack.s2.address] = MEMORY[settings.stack.s2.address] + 1 # Update stack pointer
				MEMORY[settings.stack.s2.address + StackPointer] = val
			# updateStackGUI()
		case "POPL":
			for i in range(len(Registers)-1,-1,-1): # Reverse order - [3, 2, 1, 0]
				StackPointer = MEMORY[settings.stack.s2.address]
				Registers[i] = MEMORY[settings.stack.s2.address + StackPointer]
				MEMORY[settings.stack.s2.address] = MEMORY[settings.stack.s2.address] - 1 # Update stack pointer
			# updateStackGUI()
		case "RTC":
			if JumpRegister:
				StackPointer = MEMORY[settings.stack.s1.address] # Get stack pointer
				PC = MEMORY[settings.stack.s1.address + StackPointer]-1 # Load PC from stack
				MEMORY[settings.stack.s1.address] = MEMORY[settings.stack.s1.address] - 1 # Decrease stack
			# updateStackGUI()
		case "PSHR":
			StackPointer = MEMORY[settings.stack.s2.address] = MEMORY[settings.stack.s2.address] + 1 # Update stack pointer
			MEMORY[settings.stack.s2.address + StackPointer] = Registers[instruction%4]
			# updateStackGUI()
		case "POPR":
			StackPointer = MEMORY[settings.stack.s2.address]
			Registers[instruction%4] = MEMORY[settings.stack.s2.address + StackPointer]
			MEMORY[settings.stack.s2.address] = MEMORY[settings.stack.s2.address] - 1 # Update stack pointer
			# updateStackGUI()
		case "STRR":
			MEMORY[AddrRegister] = Registers[instruction%4]
			if AddrRegister >= 0xa000 and AddrRegister <= 0xdfff:
				writeDisplayAddress(AddrRegister)
		case "STVR":
			WriteMem(Registers[instruction%4], GetVal())
		case "LDRR":
			Registers[instruction%4] = MEMORY[AddrRegister]
		case "SHLV":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] << GetVal())
		case "SHRV":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] >> GetVal())
		case "SHLA":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] << GetAddress())
		case "SHRA":
			Registers[instruction%4] = ForceValidInt(Registers[instruction%4] >> GetAddress())
		case "ADDR":
			Registers[0] = ForceValidInt(Registers[0] + Registers[instruction%4])
		case "SUBR":
			Registers[0] = ForceValidInt(Registers[0] - Registers[instruction%4])
		case "SBRR":
			Registers[0] = ForceValidInt(Registers[instruction%4] - Registers[0])
		case "SHL0":
			Registers[0] = ForceValidInt(Registers[0] << Registers[instruction%4])
		case "SHR0":
			Registers[0] = ForceValidInt(Registers[0] >> Registers[instruction%4])
		case "CZA":
			JumpRegister = GetAddress()==0
		case "CNZR":
			JumpRegister = Registers[instruction%4]!=0
		case "CZA":
			JumpRegister = GetAddress()==0
		case "CNZA":
			JumpRegister = GetAddress()!=0

		case "JCA":
			newAddr = GetVal()
			if JumpRegister:
				PC = newAddr-1
		case "JCD":
			if JumpRegister:
				PC = AddrRegister-1

		case "CCA":
			newAddr = GetVal() # Update PC with addr read before writing it to the stack
			if JumpRegister:
				StackPointer = MEMORY[settings.stack.s1.address] = MEMORY[settings.stack.s1.address] + 1 # Update stack pointer
				MEMORY[settings.stack.s1.address + StackPointer] = PC+1 # Put current PC in stack
				PC = newAddr-1 # Update PC to Address
		case "CCD":
			if JumpRegister:
				StackPointer = MEMORY[settings.stack.s1.address] = MEMORY[settings.stack.s1.address] + 1 # Update stack pointer
				MEMORY[settings.stack.s1.address + StackPointer] = PC+1 # Put current PC in stack
				PC = AddrRegister-1 # Update PC to Address
		case "CNEA":
			JumpRegister = Registers[instruction%4]!=GetAddress()
		case "CNEV":
			JumpRegister = Registers[instruction%4]!=GetVal()
		case "BRK":
			state.Break = True
		case "HLT":
			state.Halted = True
		case _:
			print("ERR:", instructionString)
			state.Done = True

	
def go():
	global state, PC, Registers, AddrRegister, JumpRegister, InstructionsProcessed
	t=0
	while not state.Done:
		state.ClockButtonPrev = state.ClockButton
		t+=1
		if t%20==0:
			eventChecks()

		if state.ResetButton:
			clearDisplay()
			PC           = 0 	# Program Counter
			AddrRegister = 0 	# Address register
			Registers = [
				0,				# Register0
				0,				# Register1
				0,				# Register2
				0,				# Register3
			]
			MEMORY[settings.stack.s1.address] = 0
			MEMORY[settings.stack.s2.address] = 0
			state.Reset()

		if state.Halted and settings.TimingMode:
			state.Done = True

		if state.Halted or state.Break:
			updateGUI()
			state.CycleClock = 0
			state.PowerSwitch = False

		if (state.PowerSwitch or (state.ClockButton == True and state.ClockButtonPrev == False) or (state.CycleClock > 0)) and not state.Halted and not state.Break:
			if state.CycleClock > 0:
				state.CycleClock -= 1

			instruction = MEMORY[PC]

			executeInstruction(instruction)
			InstructionsProcessed += 1

			if not state.Halted:
				PC += 1
try:
	startTime = time.time()
	go()
	endTime = time.time()
	elapsedTime = endTime - startTime
	# print("Elapsed time:", f'{elapsedTime:.5f}')
	# print("Instructions:", InstructionsProcessed)
	# print("Avg Sec/Instr:", np.format_float_positional(elapsedTime/InstructionsProcessed))
	# print("Avg ns/Instr:", int((elapsedTime/InstructionsProcessed)*(10**9)))
except:
	print("DUMP:")
	print("    PC:  ", PC, "\t("+Pretty(PC)+")")
	print("    R0:  ", Registers[0], "\t(" + Pretty(Registers[0])+")")
	print("    R1:  ", Registers[1], "\t(" + Pretty(Registers[1])+")")
	print("    R2:  ", Registers[2], "\t(" + Pretty(Registers[2])+")")
	print("    R3:  ", Registers[3], "\t(" + Pretty(Registers[3])+")")
	print("    Addr:", AddrRegister, "\t(" + Pretty(AddrRegister)+")")
	print("    SP1: ", MEMORY[settings.stack.s1.address], "\t(" + Pretty(MEMORY[settings.stack.s1.address])+")")
	print("    SP2: ", MEMORY[settings.stack.s2.address], "\t(" + Pretty(MEMORY[settings.stack.s2.address])+")")
	print("    JMP: ", JumpRegister)
	# print("    Memory:")
	# for add, val in enumerate(MEMORY):
	# 	if add > 0x9eff:
	# 		continue
	# 	try:
	# 		suffix = f'< {instructionSet[str((val//4)*4)+"RR" if str((val//4)*4)+"RR" in instructionSetkeys else str(val)]}' if add == PC else ""
	# 	except KeyError:
	# 		suffix = '< ?'
	# 	print("       ", "0x"+str(hex(add))[2:].zfill(4)+":", val, "\t(0x"+str(hex(val))[2:].zfill(4)+")", suffix)
	traceback.print_exc()
pygame.quit()
