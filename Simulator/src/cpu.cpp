#include <iomanip>
#include <string>
#include <fstream>
#include <set>
#include <math.h>
#include "cpu.h"

// Constants
#define WINSIZE 512
#define WINSIZESqr 262144
// Memory map
#define VideoMemory 0xb000
#define VideoPallette 0xaf80
#define VideoSettings 0xaffe
#define StackMemory 0xf000

#define InterruptTableStart 0xaf00
// #define InterruptDataStart 0xaf70

const std::string InstructionDebugging[0x100] {"NOP", "Unused", "STV", "STA", "PSHA", "POPA", "CEZA", "CNZA", "DBCA", "DBGA", "DBCV", "DBGV", "STR0", "STR1", "STR2", "STR3", "DBCR0", "DBCR1", "DBCR2", "DBCR3", "DBGR0", "DBGR1", "DBGR2", "DBGR3", "CEZR0", "CEZR1", "CEZR2", "CEZR3", "CNZR0", "CNZR1", "CNZR2", "CNZR3", "LDV0", "LDV1", "LDV2", "LDV3", "LDA0", "LDA1", "LDA2", "LDA3", "PSHR0", "PSHR1", "PSHR2", "PSHR3", "POPR0", "POPR1", "POPR2", "POPR3", "ST0AR0", "ST0AR1", "ST0AR2", "ST0AR3", "ST1AR0", "ST1AR1", "ST1AR2", "ST1AR3", "ST2AR0", "ST2AR1", "ST2AR2", "ST2AR3", "ST3AR0", "ST3AR1", "ST3AR2", "ST3AR3", "CEA0", "CEA1", "CEA2", "CEA3", "CNA0", "CNA1", "CNA2", "CNA3", "CLTA0", "CLTA1", "CLTA2", "CLTA3", "CGTA0", "CGTA1", "CGTA2", "CGTA3", "CEV0", "CEV1", "CEV2", "CEV3", "CNV0", "CNV1", "CNV2", "CNV3", "CLTV0", "CLTV1", "CLTV2", "CLTV3", "CGTV0", "CGTV1", "CGTV2", "CGTV3", "JPRD0", "JPRD1", "JPRD2", "JPRD3", "JPRC0", "JPRC1", "JPRC2", "JPRC3", "CLRD0", "CLRD1", "CLRD2", "CLRD3", "CLRC0", "CLRC1", "CLRC2", "CLRC3", "JPVD", "INTD", "RETD", "HLTD", "JPVC", "INTC", "RETC", "HLTC", "CLVD", "Unused", "Unused", "BRKD", "CLVC", "Unused", "Unused", "BRKC", "ADDA0", "ADDA1", "ADDA2", "ADDA3", "SUBA0", "SUBA1", "SUBA2", "SUBA3", "SHLA0", "SHLA1", "SHLA2", "SHLA3", "SHRA0", "SHRA1", "SHRA2", "SHRA3", "ANDA0", "ANDA1", "ANDA2", "ANDA3", "SBRA0", "SBRA1", "SBRA2", "SBRA3", "ORA0", "ORA1", "ORA2", "ORA3", "XORA0", "XORA1", "XORA2", "XORA3", "ADDV0", "ADDV1", "ADDV2", "ADDV3", "SUBV0", "SUBV1", "SUBV2", "SUBV3", "SHLV0", "SHLV1", "SHLV2", "SHLV3", "SHRV0", "SHRV1", "SHRV2", "SHRV3", "ANDV0", "ANDV1", "ANDV2", "ANDV3", "SBRV0", "SBRV1", "SBRV2", "SBRV3", "ORV0", "ORV1", "ORV2", "ORV3", "XORV0", "XORV1", "XORV2", "XORV3", "ADDR0", "ADDR1", "ADDR2", "ADDR3", "SUBR0", "SUBR1", "SUBR2", "SUBR3", "SHLR0", "SHLR1", "SHLR2", "SHLR3", "SHRR0", "SHRR1", "SHRR2", "SHRR3", "ANDR0", "ANDR1", "ANDR2", "ANDR3", "SBRR0", "SBRR1", "SBRR2", "SBRR3", "ORR0", "ORR1", "ORR2", "ORR3", "XORR0", "XORR1", "XORR2", "XORR3", "INC0", "INC1", "INC2", "INC3", "DEC0", "DEC1", "DEC2", "DEC3", "SHLO0", "SHLO1", "SHLO2", "SHLO3", "SHRO0", "SHRO1", "SHRO2", "SHRO3", "ZERO0", "ZERO1", "ZERO2", "ZERO3", "NEG0", "NEG1", "NEG2", "NEG3", "FULL0", "FULL1", "FULL2", "FULL3", "NOT0", "NOT1", "NOT2", "NOT3"};
const int InstructionDebuggingNumArgs[0x100] {0, 0, 2, 2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
const std::set <unsigned short> AllowedInterrupts {0x5e, 0x5f};
unsigned short intArg0;
unsigned short intArg1;
cpu::cpu(std::string romFile) {
	std::cout << "CPU START" << std::endl;
	romFileName = romFile;
	reset();
}

void cpu::bootloader() {
	std::cout << "CPU BOOTLOAD: ROM " << romFileName << std::endl;
	std::ifstream hexFile;
	hexFile.open(romFileName);
	int byteRead;
	int i = 0;
	if (hexFile.is_open()) {
		while (hexFile) {
			hexFile >> std::hex >> byteRead;
			MEMORY[i] = byteRead;
			i++;
		}
	} else {
		std::cout << "File not open?" << std::endl;
	}

}

void cpu::reset() {
	std::cout << "CPU RESET" << std::endl;
	t=0;
	MEMORY[VideoSettings] = 0;
	bootloader();
}

void cpu::tick() {
	if (halted)
		return;
	t++;
	instruction = MEMORY[PC];
	if (verbose)
		debug();
	executeFunction(instruction);
	PC++;
	if (needToInterrupt)
		callInterrupt();
}

void cpu::debug() {
	unsigned short instr = MEMORY[PC];
	if (PC >= 0x100 || instr == 0xd0)
		return;
	std::cout << "CPU INSTRUCTION $" << std::hex << std::setw(4) << std::setfill('0') << PC;
	if (instr < 0x100) {
		std::cout << ":" << std::setw(2) << std::setfill('0') << instr;
		std::cout << " (" << std::setw(5) << std::setfill(' ') << InstructionDebugging[instr];
		for (int i = 0; i < 2; i++) {
			if (i < InstructionDebuggingNumArgs[instr]) {
				std::cout << ":" << std::hex << std::setw(4) << std::setfill('0') << MEMORY[PC+i+1];
			} else {
				std::cout << "     ";
			}
		}
		std::cout << ")" ;
	} else {
		std::cout << ":" << std::setw(4) << std::setfill('0') << instr;
		std::cout << " (ERR          )" ;
	}
	std::cout << " | " << std::setw(4) << std::setfill('0') << R0;
	std::cout << " | " << std::setw(4) << std::setfill('0') << R1;
	std::cout << " | " << std::setw(4) << std::setfill('0') << R2;
	std::cout << " | " << std::setw(4) << std::setfill('0') << R3;
	std::cout << " | Stack[" << MEMORY[StackMemory] << "]: ";
	if (MEMORY[StackMemory] > 0xfff) {
		std::cout << " !!!!";
	} else {
		for (int i = 1; i <= MEMORY[StackMemory]; i++) {
			std::cout << " " << std::setw(4) << std::setfill('0') << MEMORY[StackMemory+i];
		}
	}
	std::cout << std::endl;
	// std::cout << "VideoMode " << MEMORY[VideoSettings] << std::endl;
	// std::cout << "Jump " << jump << std::endl;
}

int cpu::pallette16_888(unsigned short x) {
	if (x>0xf)
		std::cout << "ERR: Invalid pallete access, (" << x << ") is greater than 15." << std::endl;
	return rgb565_888(MEMORY[VideoPallette+x]);
}
int cpu::pallette2_888(unsigned short x) {
	return rgb565_888(x == 0 ? MEMORY[VideoPallette] : MEMORY[VideoPallette + 1]);
}
int cpu::rgb565_888(unsigned short x) {
	unsigned char r = x >> 11;
	unsigned char g = (x >> 5)%0b1000000;
	unsigned char b = (x >> 0)%0b100000;
	r = (r*255+15) / 31;
	g = (g*255+31) / 63;
	b = (b*255+15) / 31;
	return r*0x10000 + g*0x100 + b;
}
int cpu::drgb_888(unsigned short x) {
	if (x == 8) // dark white / light gray ends up as a special case
		return 0xc0c0c0;
	bool d = x & 0b1000;
	bool r = x & 0b0100;
	bool g = x & 0b0010;
	bool b = x & 0b0001;
	unsigned char vd = d ? 255 : 128;
	unsigned char vr = r*vd;
	unsigned char vg = g*vd;
	unsigned char vb = b*vd;
	return vr*0x10000 + vg*0x100 + vb;
	
}
int cpu::getColorAt(int x) {
	int color; // Color to display at pixel x
	int d; // Size of display in bytes
	unsigned short address; // Address in memory of video pixel
	unsigned short displayMode = MEMORY[VideoSettings];
	switch (displayMode) {
		// 128 x 128 display scaled to 512 x 512
		// rgb565 color
		case 0:
			d = 128;
			address = ((int)floor((d*x)/WINSIZE) % d) + (d * floor((d*x)/WINSIZESqr));
			color = rgb565_888(MEMORY[VideoMemory+address]);
			break;
		// 256 x 256 display scaled to 512 x 512
		// drgb color
		case 1:
			d = 256;
			address = ((int)floor((d*x)/WINSIZE) % d) + (d * floor((d*x)/WINSIZESqr));
			color = drgb_888((MEMORY[VideoMemory+address/4] >> (3-(x/2)%4)*0x4) % 0x10);
			break;
		// 256 x 256 display scaled to 512 x 512
		// 16 color pallette
		case 2:
			d = 256;
			address = ((int)floor((d*x)/WINSIZE) % d) + (d * floor((d*x)/WINSIZESqr));
			color = pallette16_888((MEMORY[VideoMemory+address/4] >> (3-(x/2)%4)*0x4) & 0xf);
			break;
		// 512 x 512 display
		// 2 color pallette
		case 3:
			color = pallette2_888((MEMORY[VideoMemory+x/0x10] >> (0xf-(x%0x10))) & 0x1);
			break;
		default:
			if (!halted)
				std::cout << "ERR: Invalid display mode (" << displayMode << ") selected." << std::endl;
			color = 0;
			halted = true;
	}
	return color;
}

unsigned short cpu::getAtAddress(unsigned short address) {
	return MEMORY[address];
}
unsigned short cpu::getArgument() {
	return MEMORY[++PC];
}
void cpu::setValueAtAddress(unsigned short value, unsigned short address) {
	MEMORY[address] = value;
}
void cpu::pushToStack(unsigned short value) {
	unsigned short addr = ++MEMORY[StackMemory];
	MEMORY[StackMemory + addr] = value;
	if (MEMORY[StackMemory] == 0) {
		std::cout << "ERR: Stack Overflow. Pushed to stack and pointer overflowed to 0" << std::endl;
		halted = true;
	}
}
unsigned short cpu::popFromStack() {
	unsigned short addr = MEMORY[StackMemory]--;
	return MEMORY[StackMemory + addr];
	if (MEMORY[StackMemory] == 0xfff) {
		std::cout << "ERR: Stack Underflow. Popped from stack and pointer under flowed to 0xfff" << std::endl;
		halted = true;
	}
}

void cpu::callInterrupt(unsigned short interrupt) {
	if (interrupt > 0x5f) {
		std::cout << "ERR: Invalid interrupt 0x" << std::hex << std::setw(2) << std::setfill('0') << value << std::endl;
		halted = true;
		return;
	}
	interruptToCall = interrupt;
	needToInterrupt = true;
}
void cpu::callInterrupt() {
	if (MEMORY[InterruptTableStart + interruptToCall] != 0) {
		pushToStack(PC-1);
		if (interruptToCall == 0x00) {
			pushToStack(R0);
			pushToStack(R1);
			pushToStack(R2);
			pushToStack(R3);
			pushToStack(intArg0);
			pushToStack(intArg1);
			// std::cout << "Stacked " << (int)intArg0 << " and then " << (int)intArg1 << "!" << std::endl;
		}
		PC = MEMORY[InterruptTableStart + interruptToCall];
		needToInterrupt = false;
	}
}

void cpu::keyStateChange(unsigned char keyCode, bool state) {
	intArg0 = keyCode;
	intArg1 = state;
	// std::cout << "Got keycode " << keyCode << std::endl;
	// std::cout << "Got keycode " << (int)keyCode << std::endl;
	callInterrupt(0x00);
}

void cpu::memLog(unsigned short from, unsigned short to) {
	std::cout << std::hex << std::setfill('0');
	std::cout << "PC:" << std::setw(4) << PC << std::endl;
	std::cout << "== 0x" << std::setw(4) << from << "-0x" << std::setw(4) << to << std::endl;
	for (int i = from; i <= to; i++) {
		std::cout << "0x" << std::setw(4) << i << ":0x" << std::setw(4) << MEMORY[i] << std::endl;
	}
}

void cpu::executeFunction(unsigned short instruction) {
	// if (instruction > 0xff) {
	// 	std::cout << "Not an instruction: " << instruction << std::endl;
	// 	halted = true;
	// }
	// if (instruction & 0x80) {								// Math
	// 	unsigned short argument;
	// 	if (instruction & 0x40) { 							// Other
	// 		if (instruction & 0x20) {						// Monadic
	// 			if (instruction & 0x10) {					// 
	// 				if (instruction & 0x08) {
	// 					argument = 0xff;					// 0xff
	// 				} else {
	// 					argument = 0x00;					// 0x00
	// 				}
	// 			} else {									// 0x01
	// 				argument = 0x01;
	// 			}
	// 		} else {										// R0
	// 			argument = R0;
	// 		}
	// 	} else {											// Immediate
	// 		if (instruction & 0x20) { 						// Address
	// 			argument = getAtAddress(getArgument());
	// 		} else {										// Value
	// 			argument = getArgument();
	// 		}
	// 	}
	// 	if (instruction & 0x00011100 == 0b00010100) {		// If SBR..
	// 		unsigned short otherArgument = argument;
	// 		argument = 
	// 	}
	// } else { 												// Other
	// }
	switch (instruction) {
	case 0x00: // NOP
		break;
	// case 0x01:
	case 0x02: // STV
		value = getArgument();
		setValueAtAddress(value, getArgument());
		break;
	case 0x03: // STA
		value = getAtAddress(getArgument());
		setValueAtAddress(value, getArgument());
		break;
	case 0x04: // PSHA
		pushToStack(R0);
		pushToStack(R1);
		pushToStack(R2);
		pushToStack(R3);
		break;
	case 0x05: // POPA
		R3 = popFromStack();
		R2 = popFromStack();
		R1 = popFromStack();
		R0 = popFromStack();
		break;
	case 0x06: // CEZA
		jump = getAtAddress(getArgument()) == 0;
		break;
	case 0x07: // CNZA
		jump = getAtAddress(getArgument()) != 0;
		break;
	case 0x08: // DBCA
		std::cout << (char)getAtAddress(getArgument());
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0x09: // DBGA
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << getAtAddress(getArgument()) << std::endl;
		break;
	case 0x0a: // DBCV
		std::cout << (char)getArgument();
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0x0b: // DBGV
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << getArgument() << std::endl;
		break;
	case 0x0c: // STR0
		setValueAtAddress(R0, getArgument());
		break;
	case 0x0d: // STR1
		setValueAtAddress(R1, getArgument());
		break;
	case 0x0e: // STR2
		setValueAtAddress(R2, getArgument());
		break;
	case 0x0f: // STR3
		setValueAtAddress(R3, getArgument());
		break;
	case 0x10: // DBCR0
		std::cout << (char)R0;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0x11: // DBCR1
		std::cout << (char)R1;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0x12: // DBCR2
		std::cout << (char)R2;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0x13: // DBCR3
		std::cout << (char)R3;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0x14: // DBGR0
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R0 << std::endl;
		break;
	case 0x15: // DBGR1
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R1 << std::endl;
		break;
	case 0x16: // DBGR2
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R2 << std::endl;
		break;
	case 0x17: // DBGR3
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R3 << std::endl;
		break;
	case 0x18: // CEZR0
		jump = R0 == 0;
		break;
	case 0x19: // CEZR1
		jump = R1 == 0;
		break;
	case 0x1a: // CEZR2
		jump = R2 == 0;
		break;
	case 0x1b: // CEZR3
		jump = R3 == 0;
		break;
	case 0x1c: // CNZR0
		jump = R0 != 0;
		break;
	case 0x1d: // CNZR1
		jump = R1 != 0;
		break;
	case 0x1e: // CNZR2
		jump = R2 != 0;
		break;
	case 0x1f: // CNZR3
		jump = R3 != 0;
		break;
	case 0x20: // LDV0
		R0 = getArgument();
		break;
	case 0x21: // LDV1
		R1 = getArgument();
		break;
	case 0x22: // LDV2
		R2 = getArgument();
		break;
	case 0x23: // LDV3
		R3 = getArgument();
		break;
	case 0x24: // LDA0
		R0 = getAtAddress(getArgument());
		break;
	case 0x25: // LDA1
		R1 = getAtAddress(getArgument());
		break;
	case 0x26: // LDA2
		R2 = getAtAddress(getArgument());
		break;
	case 0x27: // LDA3
		R3 = getAtAddress(getArgument());
		break;
	case 0x28: // PSHR0
		pushToStack(R0);
		break;
	case 0x29: // PSHR1
		pushToStack(R1);
		break;
	case 0x2a: // PSHR2
		pushToStack(R2);
		break;
	case 0x2b: // PSHR3
		pushToStack(R3);
		break;
	case 0x2c: // POPR0
		R0 = popFromStack();
		break;
	case 0x2d: // POPR1
		R1 = popFromStack();
		break;
	case 0x2e: // POPR2
		R2 = popFromStack();
		break;
	case 0x2f: // POPR3
		R3 = popFromStack();
		break;
	case 0x30: // ST0AR0
		setValueAtAddress(R0, R0);
		break;
	case 0x31: // ST0AR1
		setValueAtAddress(R0, R1);
		break;
	case 0x32: // ST0AR2
		setValueAtAddress(R0, R2);
		break;
	case 0x33: // ST0AR3
		setValueAtAddress(R0, R3);
		break;
	case 0x34: // ST1AR0
		setValueAtAddress(R1, R0);
		break;
	case 0x35: // ST1AR1
		setValueAtAddress(R1, R1);
		break;
	case 0x36: // ST1AR2
		setValueAtAddress(R1, R2);
		break;
	case 0x37: // ST1AR3
		setValueAtAddress(R1, R3);
		break;
	case 0x38: // ST2AR0
		setValueAtAddress(R2, R0);
		break;
	case 0x39: // ST2AR1
		setValueAtAddress(R2, R1);
		break;
	case 0x3a: // ST2AR2
		setValueAtAddress(R2, R2);
		break;
	case 0x3b: // ST2AR3
		setValueAtAddress(R2, R3);
		break;
	case 0x3c: // ST3AR0
		setValueAtAddress(R3, R0);
		break;
	case 0x3d: // ST3AR1
		setValueAtAddress(R3, R1);
		break;
	case 0x3e: // ST3AR2
		setValueAtAddress(R3, R2);
		break;
	case 0x3f: // ST3AR3
		setValueAtAddress(R3, R3);
		break;
	case 0x40: // CEA0
		jump = R0 == getAtAddress(getArgument());
		break;
	case 0x41: // CEA1
		jump = R1 == getAtAddress(getArgument());
		break;
	case 0x42: // CEA2
		jump = R2 == getAtAddress(getArgument());
		break;
	case 0x43: // CEA3
		jump = R3 == getAtAddress(getArgument());
		break;
	case 0x44: // CNA0
		jump = R0 != getAtAddress(getArgument());
		break;
	case 0x45: // CNA1
		jump = R1 != getAtAddress(getArgument());
		break;
	case 0x46: // CNA2
		jump = R2 != getAtAddress(getArgument());
		break;
	case 0x47: // CNA3
		jump = R3 != getAtAddress(getArgument());
		break;
	case 0x48: // CLTA0
		jump = R0 < getAtAddress(getArgument());
		break;
	case 0x49: // CLTA1
		jump = R1 < getAtAddress(getArgument());
		break;
	case 0x4a: // CLTA2
		jump = R2 < getAtAddress(getArgument());
		break;
	case 0x4b: // CLTA3
		jump = R3 < getAtAddress(getArgument());
		break;
	case 0x4c: // CGTA0
		jump = R0 > getAtAddress(getArgument());
		break;
	case 0x4d: // CGTA1
		jump = R1 > getAtAddress(getArgument());
		break;
	case 0x4e: // CGTA2
		jump = R2 > getAtAddress(getArgument());
		break;
	case 0x4f: // CGTA3
		jump = R3 > getAtAddress(getArgument());
		break;
	case 0x50: // CEV0
		jump = R0 == getArgument();
		break;
	case 0x51: // CEV1
		jump = R1 == getArgument();
		break;
	case 0x52: // CEV2
		jump = R2 == getArgument();
		break;
	case 0x53: // CEV3
		jump = R3 == getArgument();
		break;
	case 0x54: // CNV0
		jump = R0 != getArgument();
		break;
	case 0x55: // CNV1
		jump = R1 != getArgument();
		break;
	case 0x56: // CNV2
		jump = R2 != getArgument();
		break;
	case 0x57: // CNV3
		jump = R3 != getArgument();
		break;
	case 0x58: // CLTV0
		jump = R0 < getArgument();
		break;
	case 0x59: // CLTV1
		jump = R1 < getArgument();
		break;
	case 0x5a: // CLTV2
		jump = R2 < getArgument();
		break;
	case 0x5b: // CLTV3
		jump = R3 < getArgument();
		break;
	case 0x5c: // CGTV0
		jump = R0 > getArgument();
		break;
	case 0x5d: // CGTV1
		jump = R1 > getArgument();
		break;
	case 0x5e: // CGTV2
		jump = R2 > getArgument();
		break;
	case 0x5f: // CGTV3
		jump = R3 > getArgument();
		break;
	case 0x60: // JPRD0
		PC = R0-1;
		break;
	case 0x61: // JPRD1
		PC = R1-1;
		break;
	case 0x62: // JPRD2
		PC = R2-1;
		break;
	case 0x63: // JPRD3
		PC = R3-1;
		break;
	case 0x64: // JPRC0
		if(jump)
			PC = R0-1;
		break;
	case 0x65: // JPRC1
		if(jump)
			PC = R1-1;
		break;
	case 0x66: // JPRC2
		if(jump)
			PC = R2-1;
		break;
	case 0x67: // JPRC3
		if(jump)
			PC = R3-1;
		break;
	case 0x68: // CLRD0
		pushToStack(PC);
		PC = R0-1;
		break;
	case 0x69: // CLRD1
		pushToStack(PC);
		PC = R1-1;
		break;
	case 0x6a: // CLRD2
		pushToStack(PC);
		PC = R2-1;
		break;
	case 0x6b: // CLRD3
		pushToStack(PC);
		PC = R3-1;
		break;
	case 0x6c: // CLRC0
		if(jump) {
			pushToStack(PC);
			PC = R0-1;
		}
		break;
	case 0x6d: // CLRC1
		if(jump) {
			pushToStack(PC);
			PC = R1-1;
		}
		break;
	case 0x6e: // CLRC2
		if(jump) {
			pushToStack(PC);
			PC = R2-1;
		}
		break;
	case 0x6f: // CLRC3
		if(jump) {
			pushToStack(PC);
			PC = R3-1;
		}
		break;
	case 0x70: // JPVD
		PC = getArgument()-1;
		break;
	case 0x71: // INTD
		value = getArgument();
		if (value > 0x5f || AllowedInterrupts.find(value) == AllowedInterrupts.end()) {
			std::cout << "ERR: Invalid interrupt 0x" << std::hex << std::setw(2) << std::setfill('0') << value << std::endl;
			halted = true;
		} else {
			pushToStack(PC);
			PC = MEMORY[0xaf00 + value]-1;
		}
		break;
	case 0x72: // RETD
		PC = popFromStack();
		break;
	case 0x73: // HLTD
		std::cout << "\nCPU HALT" << std::endl;
		halted = true;
		break;
	case 0x74: // JPVC
		value = getArgument();
		if(jump)
			PC = value-1;
		break;
	case 0x75: // INTC
		value = getArgument();
		if (value > 0x5f || AllowedInterrupts.find(value) == AllowedInterrupts.end()) {
			std::cout << "ERR: Invalid interrupt 0x" << std::hex << std::setw(2) << std::setfill('0') << value << std::endl;
			halted = true;
		} else {
			if (jump) {
				pushToStack(PC);
				PC = MEMORY[0xaf00 + value]-1;
			}
		}
		break;
	case 0x76: // RETC
		if(jump)
			PC = popFromStack();
		break;
	case 0x77: // HLTC
		if(jump) {
			std::cout << "\nCPU HALT" << std::endl;
			halted = true;
		}
		break;
	case 0x78: // CLVD
		pushToStack(PC);
		PC = getArgument()-1;
		break;
	// case 0x79:
	// case 0x7a:
	case 0x7b: // BRKD
		std::cout << "\nCPU BREAK" << std::endl;
		broken = true;
		break;
	case 0x7c: // CLVC
		value = getArgument();
		if(jump) {
			pushToStack(PC);
			PC = value-1;
		}
		break;
	// case 0x7d:
	// case 0x7e:
	case 0x7f: // BRKC
		if(jump) {
			std::cout << "\nCPU BREAK" << std::endl;
			broken = true;
		}
		break;
	case 0x80: // ADDA0
		R0 = R0 + getAtAddress(getArgument());
		break;
	case 0x81: // ADDA1
		R1 = R1 + getAtAddress(getArgument());
		break;
	case 0x82: // ADDA2
		R2 = R2 + getAtAddress(getArgument());
		break;
	case 0x83: // ADDA3
		R3 = R3 + getAtAddress(getArgument());
		break;
	case 0x84: // SUBA0
		R0 = R0 - getAtAddress(getArgument());
		break;
	case 0x85: // SUBA1
		R1 = R1 - getAtAddress(getArgument());
		break;
	case 0x86: // SUBA2
		R2 = R2 - getAtAddress(getArgument());
		break;
	case 0x87: // SUBA3
		R3 = R3 - getAtAddress(getArgument());
		break;
	case 0x88: // SHLA0
		R0 = R0 << getAtAddress(getArgument());
		break;
	case 0x89: // SHLA1
		R1 = R1 << getAtAddress(getArgument());
		break;
	case 0x8a: // SHLA2
		R2 = R2 << getAtAddress(getArgument());
		break;
	case 0x8b: // SHLA3
		R3 = R3 << getAtAddress(getArgument());
		break;
	case 0x8c: // SHRA0
		R0 = R0 >> getAtAddress(getArgument());
		break;
	case 0x8d: // SHRA1
		R1 = R1 >> getAtAddress(getArgument());
		break;
	case 0x8e: // SHRA2
		R2 = R2 >> getAtAddress(getArgument());
		break;
	case 0x8f: // SHRA3
		R3 = R3 >> getAtAddress(getArgument());
		break;
	case 0x90: // ANDA0
		R0 = R0 & getAtAddress(getArgument());
		break;
	case 0x91: // ANDA1
		R1 = R1 & getAtAddress(getArgument());
		break;
	case 0x92: // ANDA2
		R2 = R2 & getAtAddress(getArgument());
		break;
	case 0x93: // ANDA3
		R3 = R3 & getAtAddress(getArgument());
		break;
	case 0x94: // SBRA0
		R0 = getAtAddress(getArgument()) - R0;
		break;
	case 0x95: // SBRA1
		R1 = getAtAddress(getArgument()) - R1;
		break;
	case 0x96: // SBRA2
		R2 = getAtAddress(getArgument()) - R2;
		break;
	case 0x97: // SBRA3
		R3 = getAtAddress(getArgument()) - R3;
		break;
	case 0x98: // ORA0
		R0 = R0 | getAtAddress(getArgument());
		break;
	case 0x99: // ORA1
		R1 = R1 | getAtAddress(getArgument());
		break;
	case 0x9a: // ORA2
		R2 = R2 | getAtAddress(getArgument());
		break;
	case 0x9b: // ORA3
		R3 = R3 | getAtAddress(getArgument());
		break;
	case 0x9c: // XORA0
		R0 = R0 ^ getAtAddress(getArgument());
		break;
	case 0x9d: // XORA1
		R1 = R1 ^ getAtAddress(getArgument());
		break;
	case 0x9e: // XORA2
		R2 = R2 ^ getAtAddress(getArgument());
		break;
	case 0x9f: // XORA3
		R3 = R3 ^ getAtAddress(getArgument());
		break;
	case 0xa0: // ADDV0
		R0 = R0 + getArgument();
		break;
	case 0xa1: // ADDV1
		R1 = R1 + getArgument();
		break;
	case 0xa2: // ADDV2
		R2 = R2 + getArgument();
		break;
	case 0xa3: // ADDV3
		R3 = R3 + getArgument();
		break;
	case 0xa4: // SUBV0
		R0 = R0 - getArgument();
		break;
	case 0xa5: // SUBV1
		R1 = R1 - getArgument();
		break;
	case 0xa6: // SUBV2
		R2 = R2 - getArgument();
		break;
	case 0xa7: // SUBV3
		R3 = R3 - getArgument();
		break;
	case 0xa8: // SHLV0
		R0 = R0 << getArgument();
		break;
	case 0xa9: // SHLV1
		R1 = R1 << getArgument();
		break;
	case 0xaa: // SHLV2
		R2 = R2 << getArgument();
		break;
	case 0xab: // SHLV3
		R3 = R3 << getArgument();
		break;
	case 0xac: // SHRV0
		R0 = R0 >> getArgument();
		break;
	case 0xad: // SHRV1
		R1 = R1 >> getArgument();
		break;
	case 0xae: // SHRV2
		R2 = R2 >> getArgument();
		break;
	case 0xaf: // SHRV3
		R3 = R3 >> getArgument();
		break;
	case 0xb0: // ANDV0
		R0 = R0 & getArgument();
		break;
	case 0xb1: // ANDV1
		R1 = R1 & getArgument();
		break;
	case 0xb2: // ANDV2
		R2 = R2 & getArgument();
		break;
	case 0xb3: // ANDV3
		R3 = R3 & getArgument();
		break;
	case 0xb4: // SBRV0
		R0 = getArgument() - R0;
		break;
	case 0xb5: // SBRV1
		R1 = getArgument() - R1;
		break;
	case 0xb6: // SBRV2
		R2 = getArgument() - R2;
		break;
	case 0xb7: // SBRV3
		R3 = getArgument() - R3;
		break;
	case 0xb8: // ORV0
		R0 = R0 | getArgument();
		break;
	case 0xb9: // ORV1
		R1 = R1 | getArgument();
		break;
	case 0xba: // ORV2
		R2 = R2 | getArgument();
		break;
	case 0xbb: // ORV3
		R3 = R3 | getArgument();
		break;
	case 0xbc: // XORV0
		R0 = R0 ^ getArgument();
		break;
	case 0xbd: // XORV1
		R1 = R1 ^ getArgument();
		break;
	case 0xbe: // XORV2
		R2 = R2 ^ getArgument();
		break;
	case 0xbf: // XORV3
		R3 = R3 ^ getArgument();
		break;
	case 0xc0: // ADDR0
		R0 = R0 + R0;
		break;
	case 0xc1: // ADDR1
		R0 = R0 + R1;
		break;
	case 0xc2: // ADDR2
		R0 = R0 + R2;
		break;
	case 0xc3: // ADDR3
		R0 = R0 + R3;
		break;
	case 0xc4: // SUBR0
		R0 = R0 - R0;
		break;
	case 0xc5: // SUBR1
		R0 = R0 - R1;
		break;
	case 0xc6: // SUBR2
		R0 = R0 - R2;
		break;
	case 0xc7: // SUBR3
		R0 = R0 - R3;
		break;
	case 0xc8: // SHLR0
		R0 = R0 << R0;
		break;
	case 0xc9: // SHLR1
		R0 = R0 << R1;
		break;
	case 0xca: // SHLR2
		R0 = R0 << R2;
		break;
	case 0xcb: // SHLR3
		R0 = R0 << R3;
		break;
	case 0xcc: // SHRR0
		R0 = R0 >> R0;
		break;
	case 0xcd: // SHRR1
		R0 = R0 >> R1;
		break;
	case 0xce: // SHRR2
		R0 = R0 >> R2;
		break;
	case 0xcf: // SHRR3
		R0 = R0 >> R3;
		break;
	case 0xd0: // ANDR0
		R0 = R0 & R0;
		break;
	case 0xd1: // ANDR1
		R0 = R1 & R0;
		break;
	case 0xd2: // ANDR2
		R0 = R2 & R0;
		break;
	case 0xd3: // ANDR3
		R0 = R3 & R0;
		break;
	case 0xd4: // SBRR0
		R0 = R0 - R0;
		break;
	case 0xd5: // SBRR1
		R0 = R1 - R0;
		break;
	case 0xd6: // SBRR2
		R0 = R2 - R0;
		break;
	case 0xd7: // SBRR3
		R0 = R3 - R0;
		break;
	case 0xd8: // ORR0
		R0 = R0 | R0;
		break;
	case 0xd9: // ORR1
		R0 = R1 | R0;
		break;
	case 0xda: // ORR2
		R0 = R2 | R0;
		break;
	case 0xdb: // ORR3
		R0 = R3 | R0;
		break;
	case 0xdc: // XORR0
		R0 = R0 ^ R0;
		break;
	case 0xdd: // XORR1
		R0 = R1 ^ R0;
		break;
	case 0xde: // XORR2
		R0 = R2 ^ R0;
		break;
	case 0xdf: // XORR3
		R0 = R3 ^ R0;
		break;
	case 0xe0: // INC0
		R0++;
		break;
	case 0xe1: // INC1
		R1++;
		break;
	case 0xe2: // INC2
		R2++;
		break;
	case 0xe3: // INC3
		R3++;
		break;
	case 0xe4: // DEC0
		R0--;
		break;
	case 0xe5: // DEC1
		R1--;
		break;
	case 0xe6: // DEC2
		R2--;
		break;
	case 0xe7: // DEC3
		R3--;
		break;
	case 0xe8: // SHLO0
		R0 = R0 << 1;
		break;
	case 0xe9: // SHLO1
		R1 = R1 << 1;
		break;
	case 0xea: // SHLO2
		R2 = R2 << 1;
		break;
	case 0xeb: // SHLO3
		R3 = R3 << 1;
		break;
	case 0xec: // SHRO0
		R0 = R0 >> 1;
		break;
	case 0xed: // SHRO1
		R1 = R1 >> 1;
		break;
	case 0xee: // SHRO2
		R2 = R2 >> 1;
		break;
	case 0xef: // SHRO3
		R3 = R3 >> 1;
		break;
	case 0xf0: // ZERO0
		R0 = 0;
		break;
	case 0xf1: // ZERO1
		R1 = 0;
		break;
	case 0xf2: // ZERO2
		R2 = 0;
		break;
	case 0xf3: // ZERO3
		R3 = 0;
		break;
	case 0xf4: // NEG0
		R0 = -R0;		
		break;
	case 0xf5: // NEG1
		R1 = -R1;
		break;
	case 0xf6: // NEG2
		R2 = -R2;
		break;
	case 0xf7: // NEG3
		R3 = -R3;
		break;
	case 0xf8: // FULL0
		R0 = 255;
		break;
	case 0xf9: // FULL1
		R1 = 255;
		break;
	case 0xfa: // FULL2
		R2 = 255;
		break;
	case 0xfb: // FULL3
		R3 = 255;
		break;
	case 0xfc: // NOT0
		R0 = ~R0;		break;
	case 0xfd: // NOT1
		R1 = ~R1;		break;
	case 0xfe: // NOT2
		R2 = ~R2;		break;
	case 0xff: // NOT3
		R3 = ~R3;		break;

	default:
		std::cout << "Unknown Instruction: " << instruction << std::endl;
		halted = true;
	}
}