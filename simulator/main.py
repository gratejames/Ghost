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

AbsolutePath = os.path.abspath(os.path.dirname(__file__))
FontPath = os.path.join(AbsolutePath, 'Anonymous_Pro_B.ttf')
AnonFont = pygame.font.Font(FontPath, 20)
AnonFontSmall = pygame.font.Font(FontPath, 11)

from instructionSet import instructionSet 

import configparser

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
	class ClockButton:
		def __init__(self, cfg):
			self.rect 			= pygame.Rect(*eval(cfg["Pos"]), *eval(cfg["Size"]))
	class ResetButton:
		def __init__(self, cfg):
			self.rect 			= pygame.Rect(*eval(cfg["Pos"]), *eval(cfg["Size"]))
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
			
			pos1 = eval(cfg["Stack1Pos"])
			pos2 = eval(cfg["Stack2Pos"])
			size = eval(cfg["Size"])
			reveal = int(cfg["Reveal"])
			self.s1.rect		= pygame.Rect(*pos1, *size)
			self.s1.pos			= pos1
			self.s1.width		= size[0] - reveal
			self.s2.rect		= pygame.Rect(*pos2, *size)
			self.s2.pos			= pos2
			self.s2.width		= size[0] - reveal
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

def Lmap(v, a1,b1,a2,b2, cap = True):
	x = a2 + (b2-a2)*((v-a1)/(b1-a1))
	return int(x) if not cap or x <= b2 else int(b2)
	# real value if it's good or it's not capped



def writeDisplayAddress(addr):
	color = binColor(MEMORY.get(addr, 0))

	relativeAddress = addr - settings.display.address
	x, y = relativeAddress%128, relativeAddress//128

	pixelX, pixelY = ((x*settings.display.scale)+settings.display.position[0], (y*settings.display.scale)+settings.display.position[1])
	pygame.draw.rect(screen, color, (pixelX, pixelY, settings.display.scale, settings.display.scale))

	pygame.display.update((pixelX, pixelY), (settings.display.scale,settings.display.scale))

def clearDisplay(color = (0,0,0)):
	for x,y in [(_i,_ii) for _i in range(128) for _ii in range(128)]:
		MEMORY[settings.display.address + x + (y*128)] = 0
	pygame.draw.rect(screen, color, (settings.display.position[0], settings.display.position[1], 128*settings.display.scale, 128*settings.display.scale))
	pygame.display.update(pygame.Rect(settings.display.position, (128*settings.display.scale, 128*settings.display.scale)))

def refreshDisplay():
	for x,y in [(_i,_ii) for _i in range(128) for _ii in range(128)]:
		color = binColor(MEMORY.get(settings.display.address + x + (y*128), 0))
		pixelX, pixelY = ((x*settings.display.scale)+settings.display.position[0], (y*settings.display.scale)+settings.display.position[1])
		pygame.draw.rect(screen, color, (pixelX, pixelY, settings.display.scale, settings.display.scale))
	pygame.display.update(pygame.Rect(settings.display.position, (128*settings.display.scale, 128*settings.display.scale)))




stack1SizeLast = None
stack2SizeLast = None

def updateStackGUI():
	stack1Size = Lmap(MEMORY.get(0xe000, 0), 0, 4096, 0, 80//settings.stack.refresh)
	chg1 = stack1SizeLast != stack1Size
	if chg1:
		pygame.draw.rect(screen, settings.palette.OFF, settings.stack.s1.rect)
		pygame.draw.rect(screen, settings.palette.ON,  pygame.Rect(settings.stack.s1.pos,(settings.stack.s1.width,stack1Size*settings.stack.refresh)))

	stack2Size = Lmap(MEMORY.get(0xf000, 0), 0, 4096, 0, 80//settings.stack.refresh)
	chg2 = stack2SizeLast != stack2Size
	if chg2:
		pygame.draw.rect(screen, settings.palette.OFF, settings.stack.s2.rect)
		pygame.draw.rect(screen, settings.palette.ON,  pygame.Rect(settings.stack.s2.pos,(settings.stack.s2.width,stack2Size*settings.stack.refresh)))
	
	if chg1 or chg2:
		p1 = settings.stack.s1.pos
		p2 = (settings.stack.s2.rect.x+settings.stack.s2.rect.width,settings.stack.s2.rect.y+settings.stack.s2.rect.height)
		pygame.display.update(p1,p2)

def updateGUI():
	pygame.draw.rect(screen, settings.palette.DISABLED if (state.Halted or state.Break) else settings.palette.ON if state.PowerSwitch else settings.palette.OFF, settings.PowerSwitch.rect)
	textSurface = AnonFontSmall.render("POW", False, (0, 0, 0))
	screen.blit(textSurface, (settings.PowerSwitch.rect.x+1, settings.PowerSwitch.rect.y+6))

	pygame.draw.rect(screen, settings.palette.DISABLED if state.Halted else settings.palette.ON if state.ClockButton else settings.palette.OFF, settings.ClockButton.rect)
	textSurface = AnonFontSmall.render("CLK", False, (0, 0, 0))
	screen.blit(textSurface, (settings.ClockButton.rect.x+2, settings.ClockButton.rect.y+6))

	pygame.draw.rect(screen, settings.palette.ON if state.ResetButton else settings.palette.OFF, settings.ResetButton.rect)
	textSurface = AnonFontSmall.render("RST", False, (0, 0, 0))
	screen.blit(textSurface, (settings.ResetButton.rect.x+2, settings.ResetButton.rect.y+6))
	
	pygame.display.update((10,10), (30,90))

	updateStackGUI()



screen = pygame.display.set_mode((128*settings.display.scale+50, 128*settings.display.scale+20), pygame.RESIZABLE)
pygame.display.set_caption('Ghost Computer Simulator | By Jimmy')


clock = pygame.time.Clock()

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
JumpRegister 	= False


screen.fill(settings.display.bg)
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
def Pretty(hexInt):
	return "0x"+str(hex(hexInt))[2:].zfill(4)

def go():
	global state, PC, Registers, AddrRegister, JumpRegister
	t=0
	while not state.Done:
		state.ClockButtonPrev = state.ClockButton
		if state.Halted or state.Break:
			state.PowerSwitch = False
		t+=1
		nextInput = 0
		if t%20==0:
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
						print(state.PowerSwitch)

						print("DUMP:")
						print("    PC:  ", PC, "\t(0x"+str(hex(PC))[2:].zfill(4)+")")
						print("    R0:  ", Registers[0], "\t("+Pretty(Registers[0])+")")
						print("    R1:  ", Registers[1], "\t("+Pretty(Registers[1])+")")
						print("    R2:  ", Registers[2], "\t("+Pretty(Registers[2])+")")
						print("    R3:  ", Registers[3], "\t("+Pretty(Registers[3])+")")
						print("    R3:  ", Registers[3], "\t("+Pretty(Registers[3])+")")
						print("    SP1: ", MEMORY[0xe000], "\t("+Pretty(MEMORY[0xe000])+")")
						print("    SP2: ", MEMORY[0xf000], "\t("+Pretty(MEMORY[0xf000])+")")
						print("    JMP: ", JumpRegister)
						print("    Memory:")
						for add, val in MEMORY.items():
							if add > 0x9eff:
								continue
							suffix = f'< {instructionSet[str((val//4)*4)+"RR" if str((val//4)*4)+"RR" in instructionSet.keys() else str(val)]}' if add == PC else ""
							print("       ", Pretty(add)+":", val, "\t("+Pretty(val), suffix)
					elif event.key == pygame.K_s:
						os.system('clear')
						print("Stack 1:")
						for add, val in MEMORY.items():
							if add >= 0xefff:
								continue
							if (add >= 0xe000) or add == 0xe000:
								print("    ", Pretty(add)+":", val, "\t("+Pretty(val)+")")
					elif event.key == pygame.K_d:
						os.system('clear')
						print("Stack 1:")
						for add, val in MEMORY.items():
							if add >= 0xffff:
								continue
							if (add >= 0xf000) or add == 0xf000:
								print("    ", Pretty(add)+":", val, "\t("+Pretty(val)+")")
					elif event.key == pygame.K_SPACE:
						state.CycleClock = 1
					elif event.key == pygame.K_1:
						state.CycleClock = 10
					elif event.key == pygame.K_2:
						state.CycleClock = 100
					elif event.key == pygame.K_3:
						state.CycleClock = 1000


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
			MEMORY[0xe000] = 0
			MEMORY[0xf000] = 0
			state.Reset()

		if state.Halted and settings.TimingMode:
			state.Done = True

		if state.Halted or state.Break:
			updateGUI()
			state.CycleClock = 0

		if (state.PowerSwitch or (state.ClockButton == True and state.ClockButtonPrev == False) or (state.CycleClock > 0)) and not state.Halted and not state.Break:
			if state.CycleClock > 0:
				state.CycleClock -= 1

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
				updateStackGUI()
			elif instructionString == "CALA":
				StackPointer = MEMORY[0xe000] = MEMORY[0xe000] + 1 # Update stack pointer
				newAddr = GetVal() # Update PC with addr read before writing it to the stack
				MEMORY[0xe000 + StackPointer] = PC+1 # Put current PC in stack
				PC = newAddr-1 # Update PC to Address
				updateStackGUI()
			elif instructionString == "RT":
				StackPointer = MEMORY[0xe000] # Get stack pointer
				PC = MEMORY[0xe000 + StackPointer]-1 # Load PC from stack
				MEMORY[0xe000] = MEMORY[0xe000] - 1 # Decrease stack
				updateStackGUI()
			elif instructionString == "PSHL":
				for val in Registers:
					StackPointer = MEMORY[0xf000] = MEMORY[0xf000] + 1 # Update stack pointer
					MEMORY[0xf000 + StackPointer] = val
				updateStackGUI()
			elif instructionString == "POPL":
				for i in range(len(Registers)-1,-1,-1): # Reverse order - [3, 2, 1, 0]
					StackPointer = MEMORY[0xf000]
					Registers[i] = MEMORY[0xf000 + StackPointer]
					MEMORY[0xf000] = MEMORY[0xf000] - 1 # Update stack pointer
				updateStackGUI()
			elif instructionString == "RTC":
				if JumpRegister:
					StackPointer = MEMORY[0xe000] # Get stack pointer
					PC = MEMORY[0xe000 + StackPointer]-1 # Load PC from stack
					MEMORY[0xe000] = MEMORY[0xe000] - 1 # Decrease stack
				updateStackGUI()
			elif instructionString == "PSHR":
				StackPointer = MEMORY[0xf000] = MEMORY[0xf000] + 1 # Update stack pointer
				MEMORY[0xf000 + StackPointer] = Registers[instruction%4]
				updateStackGUI()
			elif instructionString == "POPR":
				StackPointer = MEMORY[0xf000]
				Registers[instruction%4] = MEMORY[0xf000 + StackPointer]
				MEMORY[0xf000] = MEMORY[0xf000] - 1 # Update stack pointer
				updateStackGUI()
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
			elif instructionString == "CCD":
				if JumpRegister:
					StackPointer = MEMORY[0xe000] = MEMORY[0xe000] + 1 # Update stack pointer
					MEMORY[0xe000 + StackPointer] = PC+1 # Put current PC in stack
					PC = AddrRegister-1 # Update PC to Address

			elif instructionString == "CNEA":
				JumpRegister = Registers[instruction%4]!=GetAddress()
			elif instructionString == "CNEV":
				JumpRegister = Registers[instruction%4]!=GetVal()

			elif instructionString == "BRK":
				state.Break = True
			elif instructionString == "HLT":
				state.Halted = True
			else:
				print("ERR:", instructionString)
				state.Done = True

			for i in range(len(Registers)):
				Registers[i] = Registers[i]%0x10000

			if not state.Halted:
				PC += 1
try:
	go()
except:
	print("DUMP:")
	print("    PC:  ", PC, "\t("+Pretty(PC)+")")
	print("    R0:  ", Registers[0], "\t(" + Pretty(Registers[0])+")")
	print("    R1:  ", Registers[1], "\t(" + Pretty(Registers[1])+")")
	print("    R2:  ", Registers[2], "\t(" + Pretty(Registers[2])+")")
	print("    R3:  ", Registers[3], "\t(" + Pretty(Registers[3])+")")
	print("    Addr:", AddrRegister, "\t(" + Pretty(AddrRegister)+")")
	print("    SP1: ", MEMORY[0xe000], "\t(" + Pretty(MEMORY[0xe000])+")")
	print("    SP2: ", MEMORY[0xf000], "\t(" + Pretty(MEMORY[0xf000])+")")
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
