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
#define InterruptDataStart 0xaf70

const std::string InstructionDebugging[0x100] {"NOP", "MVAA", "DDV", "DDA", "DDR0", "DDR1", "DDR2", "DDR3", "LDV0", "LDV1", "LDV2", "LDV3", "LDA0", "LDA1", "LDA2", "LDA3", "LDD0", "LDD1", "LDD2", "LDD3", "STR0", "STR1", "STR2", "STR3", "STAR0", "STAR1", "STAR2", "STAR3", "STV", "STDV", "MVDD", "INT", "STDR0", "STDR1", "STDR2", "STDR3", "SHLV0", "SHLV1", "SHLV2", "SHLV3", "SHLA0", "SHLA1", "SHLA2", "SHLA3", "SHLR0", "SHLR1", "SHLR2", "SHLR3", "SHRV0", "SHRV1", "SHRV2", "SHRV3", "SHRA0", "SHRA1", "SHRA2", "SHRA3", "SHRR0", "SHRR1", "SHRR2", "SHRR3", "ADDV0", "ADDV1", "ADDV2", "ADDV3", "ADDA0", "ADDA1", "ADDA2", "ADDA3", "ADDR0", "ADDR1", "ADDR2", "ADDR3", "SUBV0", "SUBV1", "SUBV2", "SUBV3", "SUBA0", "SUBA1", "SUBA2", "SUBA3", "SUBR0", "SUBR1", "SUBR2", "SUBR3", "SBRV0", "SBRV1", "SBRV2", "SBRV3", "SBRA0", "SBRA1", "SBRA2", "SBRA3", "SBRR0", "SBRR1", "SBRR2", "SBRR3", "NOT0", "NOT1", "NOT2", "NOT3", "NEG0", "NEG1", "NEG2", "NEG3", "INC0", "INC1", "INC2", "INC3", "DEC0", "DEC1", "DEC2", "DEC3", "SHLO0", "SHLO1", "SHLO2", "SHLO3", "SHRO0", "SHRO1", "SHRO2", "SHRO3", "ANDV0", "ANDV1", "ANDV2", "ANDV3", "ANDA0", "ANDA1", "ANDA2", "ANDA3", "ANDR0", "ANDR1", "ANDR2", "ANDR3", "ORV0", "ORV1", "ORV2", "ORV3", "ORA0", "ORA1", "ORA2", "ORA3", "ORR0", "ORR1", "ORR2", "ORR3", "XORV0", "XORV1", "XORV2", "XORV3", "XORA0", "XORA1", "XORA2", "XORA3", "XORR0", "XORR1", "XORR2", "XORR3", "PSHR0", "PSHR1", "PSHR2", "PSHR3", "POPR0", "POPR1", "POPR2", "POPR3", "PSHA", "POPA", "CEZA", "CNZA", "CEZR0", "CEZR1", "CEZR2", "CEZR3", "CNZR0", "CNZR1", "CNZR2", "CNZR3", "CEV0", "CEV1", "CEV2", "CEV3", "CEA0", "CEA1", "CEA2", "CEA3", "CNV0", "CNV1", "CNV2", "CNV3", "CNA0", "CNA1", "CNA2", "CNA3", "CLTV0", "CLTV1", "CLTV2", "CLTV3", "CLTA0", "CLTA1", "CLTA2", "CLTA3", "CGTV0", "CGTV1", "CGTV2", "CGTV3", "CGTA0", "CGTA1", "CGTA2", "CGTA3", "JMPA", "JMPD", "CALA", "CALD", "RET", "JPCA", "JPCD", "CLCA", "CLCD", "RETC", "BRK", "HLT", "DBGR0", "DBGR1", "DBGR2", "DBGR3", "DBGV", "DBGA", "DBCA", "DBCV", "DBCR0", "DBCR1", "DBCR2", "DBCR3", "ADOR0", "ADOR1", "ADOR2", "ADOR3", "ADOV", "ADOA", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused", "Unused"};
const int InstructionDebuggingNumArgs[0x100] {0, 2, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
const std::set <unsigned short> AllowedInterrupts {0x5e, 0x5f};

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
	if (instr == 0xd0)
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
	pushToStack(PC-1);
	PC = MEMORY[InterruptTableStart + interruptToCall];
	needToInterrupt = false;
}

void cpu::keyStateChange(unsigned char keyCode, bool state) {
	// std::cout << "Got keycode " << keyCode << std::endl;
	// std::cout << "Got keycode " << (int)keyCode << std::endl;
	setValueAtAddress(keyCode, InterruptDataStart+0);
	setValueAtAddress(state, InterruptDataStart+1);
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
	switch (instruction) {
	case 0x00: // NOP
		break;
	case 0x01: // MVAA
		value = getAtAddress(getArgument());
		setValueAtAddress(value, getArgument());
		break;
	case 0x02: // DDV
		DD = getArgument();
		break;
	case 0x03: // DDA
		DD = getAtAddress(getArgument());
		break;
	case 0x04: // DDR0
		DD = R0;
		break;
	case 0x05: // DDR1
		DD = R1;
		break;
	case 0x06: // DDR2
		DD = R2;
		break;
	case 0x07: // DDR3
		DD = R3;
		break;
	case 0x08: // LDV0
		R0 = getArgument();
		break;
	case 0x09: // LDV1
		R1 = getArgument();
		break;
	case 0x0a: // LDV2
		R2 = getArgument();
		break;
	case 0x0b: // LDV3
		R3 = getArgument();
		break;
	case 0x0c: // LDA0
		R0 = getAtAddress(getArgument());
		break;
	case 0x0d: // LDA1
		R1 = getAtAddress(getArgument());
		break;
	case 0x0e: // LDA2
		R2 = getAtAddress(getArgument());
		break;
	case 0x0f: // LDA3
		R3 = getAtAddress(getArgument());
		break;
	case 0x10: // LDD0
		R0 = getAtAddress(DD);
		break;
	case 0x11: // LDD1
		R1 = getAtAddress(DD);
		break;
	case 0x12: // LDD2
		R2 = getAtAddress(DD);
		break;
	case 0x13: // LDD3
		R3 = getAtAddress(DD);
		break;
	case 0x14: // STR0
		setValueAtAddress(R0, getArgument());
		break;
	case 0x15: // STR1
		setValueAtAddress(R1, getArgument());
		break;
	case 0x16: // STR2
		setValueAtAddress(R2, getArgument());
		break;
	case 0x17: // STR3
		setValueAtAddress(R3, getArgument());
		break;
	case 0x18: // STAR0
		setValueAtAddress(getArgument(), R0);
		break;
	case 0x19: // STAR1
		setValueAtAddress(getArgument(), R1);
		break;
	case 0x1a: // STAR2
		setValueAtAddress(getArgument(), R2);
		break;
	case 0x1b: // STAR3
		setValueAtAddress(getArgument(), R3);
		break;
	case 0x1c: // STV
		value = getArgument();
		setValueAtAddress(value, getArgument());
		break;
	case 0x1d: // STDV
		setValueAtAddress(getArgument(), DD);
		break;
	case 0x1e: // MVDD
		setValueAtAddress(getAtAddress(DD), getArgument());
		break;
	case 0x1f: // INT
		value = getArgument();
		if (value > 0x5f || AllowedInterrupts.find(value) == AllowedInterrupts.end()) {
			std::cout << "ERR: Invalid interrupt 0x" << std::hex << std::setw(2) << std::setfill('0') << value << std::endl;
			halted = true;
		} else {
			pushToStack(PC);
			PC = MEMORY[0xaf00 + value]-1;
		}
		break;
	case 0x20: // STDR0
		setValueAtAddress(R0, DD);
		break;
	case 0x21: // STDR1
		setValueAtAddress(R1, DD);
		break;
	case 0x22: // STDR2
		setValueAtAddress(R2, DD);
		break;
	case 0x23: // STDR3
		setValueAtAddress(R3, DD);
		break;
	case 0x24: // SHLV0
		R0 = R0 << getArgument();
		break;
	case 0x25: // SHLV1
		R1 = R1 << getArgument();
		break;
	case 0x26: // SHLV2
		R2 = R2 << getArgument();
		break;
	case 0x27: // SHLV3
		R3 = R3 << getArgument();
		break;
	case 0x28: // SHLA0
		R0 = R0 << getAtAddress(getArgument());
		break;
	case 0x29: // SHLA1
		R1 = R1 << getAtAddress(getArgument());
		break;
	case 0x2a: // SHLA2
		R2 = R2 << getAtAddress(getArgument());
		break;
	case 0x2b: // SHLA3
		R3 = R3 << getAtAddress(getArgument());
		break;
	case 0x2c: // SHLR0
		R0 = R0 << R0;
		break;
	case 0x2d: // SHLR1
		R0 = R0 << R1;
		break;
	case 0x2e: // SHLR2
		R0 = R0 << R2;
		break;
	case 0x2f: // SHLR3
		R0 = R0 << R3;
		break;
	case 0x30: // SHRV0
		R0 = R0 >> getArgument();
		break;
	case 0x31: // SHRV1
		R1 = R1 >> getArgument();
		break;
	case 0x32: // SHRV2
		R2 = R2 >> getArgument();
		break;
	case 0x33: // SHRV3
		R3 = R3 >> getArgument();
		break;
	case 0x34: // SHRA0
		R0 = R0 >> getAtAddress(getArgument());
		break;
	case 0x35: // SHRA1
		R1 = R1 >> getAtAddress(getArgument());
		break;
	case 0x36: // SHRA2
		R2 = R2 >> getAtAddress(getArgument());
		break;
	case 0x37: // SHRA3
		R3 = R3 >> getAtAddress(getArgument());
		break;
	case 0x38: // SHRR0
		R0 = R0 >> R0;
		break;
	case 0x39: // SHRR1
		R0 = R0 >> R1;
		break;
	case 0x3a: // SHRR2
		R0 = R0 >> R2;
		break;
	case 0x3b: // SHRR3
		R0 = R0 >> R3;
		break;
	case 0x3c: // ADDV0
		R0 = R0 + getArgument();
		break;
	case 0x3d: // ADDV1
		R1 = R1 + getArgument();
		break;
	case 0x3e: // ADDV2
		R2 = R2 + getArgument();
		break;
	case 0x3f: // ADDV3
		R3 = R3 + getArgument();
		break;
	case 0x40: // ADDA0
		R0 = R0 + getAtAddress(getArgument());
		break;
	case 0x41: // ADDA1
		R1 = R1 + getAtAddress(getArgument());
		break;
	case 0x42: // ADDA2
		R2 = R2 + getAtAddress(getArgument());
		break;
	case 0x43: // ADDA3
		R3 = R3 + getAtAddress(getArgument());
		break;
	case 0x44: // ADDR0
		R0 = R0 + R0;
		break;
	case 0x45: // ADDR1
		R0 = R0 + R1;
		break;
	case 0x46: // ADDR2
		R0 = R0 + R2;
		break;
	case 0x47: // ADDR3
		R0 = R0 + R3;
		break;
	case 0x48: // SUBV0
		R0 = R0 - getArgument();
		break;
	case 0x49: // SUBV1
		R1 = R1 - getArgument();
		break;
	case 0x4a: // SUBV2
		R2 = R2 - getArgument();
		break;
	case 0x4b: // SUBV3
		R3 = R3 - getArgument();
		break;
	case 0x4c: // SUBA0
		R0 = R0 - getAtAddress(getArgument());
		break;
	case 0x4d: // SUBA1
		R1 = R1 - getAtAddress(getArgument());
		break;
	case 0x4e: // SUBA2
		R2 = R2 - getAtAddress(getArgument());
		break;
	case 0x4f: // SUBA3
		R3 = R3 - getAtAddress(getArgument());
		break;
	case 0x50: // SUBR0
		R0 = R0 - R0;
		break;
	case 0x51: // SUBR1
		R0 = R0 - R1;
		break;
	case 0x52: // SUBR2
		R0 = R0 - R2;
		break;
	case 0x53: // SUBR3
		R0 = R0 - R3;
		break;
	case 0x54: // SBRV0
		R0 = getArgument() - R0;
		break;
	case 0x55: // SBRV1
		R1 = getArgument() - R1;
		break;
	case 0x56: // SBRV2
		R2 = getArgument() - R2;
		break;
	case 0x57: // SBRV3
		R3 = getArgument() - R3;
		break;
	case 0x58: // SBRA0
		R0 = getAtAddress(getArgument()) - R0;
		break;
	case 0x59: // SBRA1
		R1 = getAtAddress(getArgument()) - R1;
		break;
	case 0x5a: // SBRA2
		R2 = getAtAddress(getArgument()) - R2;
		break;
	case 0x5b: // SBRA3
		R3 = getAtAddress(getArgument()) - R3;
		break;
	case 0x5c: // SBRR0
		R0 = R0 - R0;
		break;
	case 0x5d: // SBRR1
		R0 = R1 - R0;
		break;
	case 0x5e: // SBRR2
		R0 = R2 - R0;
		break;
	case 0x5f: // SBRR3
		R0 = R3 - R0;
		break;
	case 0x60: // NOT0
		R0 = ~R0;		break;
	case 0x61: // NOT1
		R1 = ~R1;		break;
	case 0x62: // NOT2
		R2 = ~R2;		break;
	case 0x63: // NOT3
		R3 = ~R3;		break;
	case 0x64: // NEG0
		R0 = -R0;		break;
	case 0x65: // NEG1
		R1 = -R1;		break;
	case 0x66: // NEG2
		R2 = -R2;		break;
	case 0x67: // NEG3
		R3 = -R3;		break;
	case 0x68: // INC0
		R0++;
		break;
	case 0x69: // INC1
		R1++;
		break;
	case 0x6a: // INC2
		R2++;
		break;
	case 0x6b: // INC3
		R3++;
		break;
	case 0x6c: // DEC0
		R0--;
		break;
	case 0x6d: // DEC1
		R1--;
		break;
	case 0x6e: // DEC2
		R2--;
		break;
	case 0x6f: // DEC3
		R3--;
		break;
	case 0x70: // SHLO0
		R0 = R0 << 1;
		break;
	case 0x71: // SHLO1
		R1 = R1 << 1;
		break;
	case 0x72: // SHLO2
		R2 = R2 << 1;
		break;
	case 0x73: // SHLO3
		R3 = R3 << 1;
		break;
	case 0x74: // SHRO0
		R0 = R0 >> 1;
		break;
	case 0x75: // SHRO1
		R1 = R1 >> 1;
		break;
	case 0x76: // SHRO2
		R2 = R2 >> 1;
		break;
	case 0x77: // SHRO3
		R3 = R3 >> 1;
		break;
	case 0x78: // ANDV0
		R0 = R0 & getArgument();
		break;
	case 0x79: // ANDV1
		R1 = R1 & getArgument();
		break;
	case 0x7a: // ANDV2
		R2 = R2 & getArgument();
		break;
	case 0x7b: // ANDV3
		R3 = R3 & getArgument();
		break;
	case 0x7c: // ANDA0
		R0 = R0 & getAtAddress(getArgument());
		break;
	case 0x7d: // ANDA1
		R1 = R1 & getAtAddress(getArgument());
		break;
	case 0x7e: // ANDA2
		R2 = R2 & getAtAddress(getArgument());
		break;
	case 0x7f: // ANDA3
		R3 = R3 & getAtAddress(getArgument());
		break;
	case 0x80: // ANDR0
		R0 = R0 & R0;
		break;
	case 0x81: // ANDR1
		R0 = R1 & R0;
		break;
	case 0x82: // ANDR2
		R0 = R2 & R0;
		break;
	case 0x83: // ANDR3
		R0 = R3 & R0;
		break;
	case 0x84: // ORV0
		R0 = R0 | getArgument();
		break;
	case 0x85: // ORV1
		R1 = R1 | getArgument();
		break;
	case 0x86: // ORV2
		R2 = R2 | getArgument();
		break;
	case 0x87: // ORV3
		R3 = R3 | getArgument();
		break;
	case 0x88: // ORA0
		R0 = R0 | getAtAddress(getArgument());
		break;
	case 0x89: // ORA1
		R1 = R1 | getAtAddress(getArgument());
		break;
	case 0x8a: // ORA2
		R2 = R2 | getAtAddress(getArgument());
		break;
	case 0x8b: // ORA3
		R3 = R3 | getAtAddress(getArgument());
		break;
	case 0x8c: // ORR0
		R0 = R0 | R0;
		break;
	case 0x8d: // ORR1
		R0 = R1 | R0;
		break;
	case 0x8e: // ORR2
		R0 = R2 | R0;
		break;
	case 0x8f: // ORR3
		R0 = R3 | R0;
		break;
	case 0x90: // XORV0
		R0 = R0 ^ getArgument();
		break;
	case 0x91: // XORV1
		R1 = R1 ^ getArgument();
		break;
	case 0x92: // XORV2
		R2 = R2 ^ getArgument();
		break;
	case 0x93: // XORV3
		R3 = R3 ^ getArgument();
		break;
	case 0x94: // XORA0
		R0 = R0 ^ getAtAddress(getArgument());
		break;
	case 0x95: // XORA1
		R1 = R1 ^ getAtAddress(getArgument());
		break;
	case 0x96: // XORA2
		R2 = R2 ^ getAtAddress(getArgument());
		break;
	case 0x97: // XORA3
		R3 = R3 ^ getAtAddress(getArgument());
		break;
	case 0x98: // XORR0
		R0 = R0 ^ R0;
		break;
	case 0x99: // XORR1
		R0 = R1 ^ R0;
		break;
	case 0x9a: // XORR2
		R0 = R2 ^ R0;
		break;
	case 0x9b: // XORR3
		R0 = R3 ^ R0;
		break;
	case 0x9c: // PSHR0
		pushToStack(R0);
		break;
	case 0x9d: // PSHR1
		pushToStack(R1);
		break;
	case 0x9e: // PSHR2
		pushToStack(R2);
		break;
	case 0x9f: // PSHR3
		pushToStack(R3);
		break;
	case 0xa0: // POPR0
		R0 = popFromStack();
		break;
	case 0xa1: // POPR1
		R1 = popFromStack();
		break;
	case 0xa2: // POPR2
		R2 = popFromStack();
		break;
	case 0xa3: // POPR3
		R3 = popFromStack();
		break;
	case 0xa4: // PSHA
		pushToStack(R0);
		pushToStack(R1);
		pushToStack(R2);
		pushToStack(R3);
		break;
	case 0xa5: // POPA
		R3 = popFromStack();
		R2 = popFromStack();
		R1 = popFromStack();
		R0 = popFromStack();
		break;
	case 0xa6: // CEZA
		jump = getAtAddress(getArgument()) == 0;
		break;
	case 0xa7: // CNZA
		jump = getAtAddress(getArgument()) != 0;
		break;
	case 0xa8: // CEZR0
		jump = R0 == 0;
		break;
	case 0xa9: // CEZR1
		jump = R1 == 0;
		break;
	case 0xaa: // CEZR2
		jump = R2 == 0;
		break;
	case 0xab: // CEZR3
		jump = R3 == 0;
		break;
	case 0xac: // CNZR0
		jump = R0 != 0;
		break;
	case 0xad: // CNZR1
		jump = R1 != 0;
		break;
	case 0xae: // CNZR2
		jump = R2 != 0;
		break;
	case 0xaf: // CNZR3
		jump = R3 != 0;
		break;
	case 0xb0: // CEV0
		jump = R0 == getArgument();
		break;
	case 0xb1: // CEV1
		jump = R1 == getArgument();
		break;
	case 0xb2: // CEV2
		jump = R2 == getArgument();
		break;
	case 0xb3: // CEV3
		jump = R3 == getArgument();
		break;
	case 0xb4: // CEA0
		jump = R0 == getAtAddress(getArgument());
		break;
	case 0xb5: // CEA1
		jump = R1 == getAtAddress(getArgument());
		break;
	case 0xb6: // CEA2
		jump = R2 == getAtAddress(getArgument());
		break;
	case 0xb7: // CEA3
		jump = R3 == getAtAddress(getArgument());
		break;
	case 0xb8: // CNV0
		jump = R0 != getArgument();
		break;
	case 0xb9: // CNV1
		jump = R1 != getArgument();
		break;
	case 0xba: // CNV2
		jump = R2 != getArgument();
		break;
	case 0xbb: // CNV3
		jump = R3 != getArgument();
		break;
	case 0xbc: // CNA0
		jump = R0 != getAtAddress(getArgument());
		break;
	case 0xbd: // CNA1
		jump = R1 != getAtAddress(getArgument());
		break;
	case 0xbe: // CNA2
		jump = R2 != getAtAddress(getArgument());
		break;
	case 0xbf: // CNA3
		jump = R3 != getAtAddress(getArgument());
		break;
	case 0xc0: // CLTV0
		jump = R0 < getArgument();
		break;
	case 0xc1: // CLTV1
		jump = R1 < getArgument();
		break;
	case 0xc2: // CLTV2
		jump = R2 < getArgument();
		break;
	case 0xc3: // CLTV3
		jump = R3 < getArgument();
		break;
	case 0xc4: // CLTA0
		jump = R0 < getAtAddress(getArgument());
		break;
	case 0xc5: // CLTA1
		jump = R1 < getAtAddress(getArgument());
		break;
	case 0xc6: // CLTA2
		jump = R2 < getAtAddress(getArgument());
		break;
	case 0xc7: // CLTA3
		jump = R3 < getAtAddress(getArgument());
		break;
	case 0xc8: // CGTV0
		jump = R0 > getArgument();
		break;
	case 0xc9: // CGTV1
		jump = R1 > getArgument();
		break;
	case 0xca: // CGTV2
		jump = R2 > getArgument();
		break;
	case 0xcb: // CGTV3
		jump = R3 > getArgument();
		break;
	case 0xcc: // CGTA0
		jump = R0 > getAtAddress(getArgument());
		break;
	case 0xcd: // CGTA1
		jump = R1 > getAtAddress(getArgument());
		break;
	case 0xce: // CGTA2
		jump = R2 > getAtAddress(getArgument());
		break;
	case 0xcf: // CGTA3
		jump = R3 > getAtAddress(getArgument());
		break;
	case 0xd0: // JMPA
		PC = getArgument()-1;
		break;
	case 0xd1: // JMPD
		PC = DD-1;
		break;
	case 0xd2: // CALA
		pushToStack(PC);
		PC = getArgument()-1;
		break;
	case 0xd3: // CALD
		pushToStack(PC);
		PC = DD-1;
		break;
	case 0xd4: // RET
		PC = popFromStack();
		break;
	case 0xd5: // JPCA
		value = getArgument();
		if(jump)
			PC = value-1;
		break;
	case 0xd6: // JPCD
		if(jump)
			PC = DD-1;
		break;
	case 0xd7: // CLCA
		value = getArgument();
		if(jump) {
			pushToStack(PC);
			PC = value-1;
		}
		break;
	case 0xd8: // CLCD
		if(jump) {
			pushToStack(PC);
			PC = DD-1;
		}
		break;
	case 0xd9: // RETC
		if(jump)
			PC = popFromStack();
		break;
	case 0xda: // BRK
		std::cout << "\nCPU BREAK" << std::endl;
		broken = true;
		break;
	case 0xdb: // HLT
		std::cout << "\nCPU HALT" << std::endl;
		halted = true;
		break;
	case 0xdc: // DBGR0
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R0 << std::endl;
		break;
	case 0xdd: // DBGR1
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R1 << std::endl;
		break;
	case 0xde: // DBGR2
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R2 << std::endl;
		break;
	case 0xdf: // DBGR3
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R3 << std::endl;
		break;
	case 0xe0: // DBGV
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << getArgument() << std::endl;
		break;
	case 0xe1: // DBGA
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << getAtAddress(getArgument()) << std::endl;
		break;
	case 0xe2: // DBCA
		std::cout << (char)getAtAddress(getArgument());
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0xe3: // DBCV
		std::cout << (char)getArgument();
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0xe4: // DBCR0
		std::cout << (char)R0;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0xe5: // DBCR1
		std::cout << (char)R1;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0xe6: // DBCR2
		std::cout << (char)R2;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0xe7: // DBCR3
		std::cout << (char)R3;
		if (flushDebugChar)
			std::cout << std::endl;
		break;
	case 0xe8: // ADOR0
		offsetRegister = R0;
		break;
	case 0xe9: // ADOR1
		offsetRegister = R1;
		break;
	case 0xea: // ADOR2
		offsetRegister = R2;
		break;
	case 0xeb: // ADOR3
		offsetRegister = R3;
		break;
	case 0xec: // ADOV
		offsetRegister = getArgument();
		break;
	case 0xed: // ADOA
		offsetRegister = getAtAddress(getArgument());
		break;
	// case 0xee:
	// case 0xef:
	// case 0xf0:
	// case 0xf1:
	// case 0xf2:
	// case 0xf3:
	// case 0xf4:
	// case 0xf5:
	// case 0xf6:
	// case 0xf7:
	// case 0xf8:
	// case 0xf9:
	// case 0xfa:
	// case 0xfb:
	// case 0xfc:
	// case 0xfd:
	// case 0xfe:
	// case 0xff:
	default:
		std::cout << "Unknown Instruction: " << instruction << std::endl;
		halted = true;
	}
}