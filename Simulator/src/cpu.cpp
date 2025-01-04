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
#define VideoPallette 0xaff0
#define VideoSettings 0xafef
#define StackMemory 0xf000

#define InterruptTableStart 0xaf00
#define IODataStart 0xafd0

// The below variables are updated by a script when the instruction set is changed. Don't change those two lines please.
// The script is at Ghost/Docs/Instruction Set.py
const std::string InstructionDebugging[0x100] {"NOP", "MVAA", "DDV", "DDA", "DDR0", "DDR1", "DDR2", "DDR3", "LDV0", "LDV1", "LDV2", "LDV3", "LDA0", "LDA1", "LDA2", "LDA3", "LDD0", "LDD1", "LDD2", "LDD3", "STR0", "STR1", "STR2", "STR3", "STAR0", "STAR1", "STAR2", "STAR3", "STV", "STDV", "MVDD", "INT", "STDR0", "STDR1", "STDR2", "STDR3", "SHLV0", "SHLV1", "SHLV2", "SHLV3", "SHLA0", "SHLA1", "SHLA2", "SHLA3", "SHLR0", "SHLR1", "SHLR2", "SHLR3", "SHRV0", "SHRV1", "SHRV2", "SHRV3", "SHRA0", "SHRA1", "SHRA2", "SHRA3", "SHRR0", "SHRR1", "SHRR2", "SHRR3", "ADDV0", "ADDV1", "ADDV2", "ADDV3", "ADDA0", "ADDA1", "ADDA2", "ADDA3", "ADDR0", "ADDR1", "ADDR2", "ADDR3", "SUBV0", "SUBV1", "SUBV2", "SUBV3", "SUBA0", "SUBA1", "SUBA2", "SUBA3", "SUBR0", "SUBR1", "SUBR2", "SUBR3", "SBRV0", "SBRV1", "SBRV2", "SBRV3", "SBRA0", "SBRA1", "SBRA2", "SBRA3", "SBRR0", "SBRR1", "SBRR2", "SBRR3", "NOT0", "NOT1", "NOT2", "NOT3", "NEG0", "NEG1", "NEG2", "NEG3", "INC0", "INC1", "INC2", "INC3", "DEC0", "DEC1", "DEC2", "DEC3", "SHLO0", "SHLO1", "SHLO2", "SHLO3", "SHRO0", "SHRO1", "SHRO2", "SHRO3", "ANDV0", "ANDV1", "ANDV2", "ANDV3", "ANDA0", "ANDA1", "ANDA2", "ANDA3", "ANDR0", "ANDR1", "ANDR2", "ANDR3", "ORV0", "ORV1", "ORV2", "ORV3", "ORA0", "ORA1", "ORA2", "ORA3", "ORR0", "ORR1", "ORR2", "ORR3", "XORV0", "XORV1", "XORV2", "XORV3", "XORA0", "XORA1", "XORA2", "XORA3", "XORR0", "XORR1", "XORR2", "XORR3", "LDZ0", "LDZ1", "LDZ2", "LDZ3", "STZ0", "STZ1", "STZ2", "STZ3", "PSHR0", "PSHR1", "PSHR2", "PSHR3", "POPR0", "POPR1", "POPR2", "POPR3", "PSHA", "POPA", "CEZA", "CNZA", "CEZR0", "CEZR1", "CEZR2", "CEZR3", "CNZR0", "CNZR1", "CNZR2", "CNZR3", "CEV0", "CEV1", "CEV2", "CEV3", "CEA0", "CEA1", "CEA2", "CEA3", "CNV0", "CNV1", "CNV2", "CNV3", "CNA0", "CNA1", "CNA2", "CNA3", "CLTV0", "CLTV1", "CLTV2", "CLTV3", "CLTA0", "CLTA1", "CLTA2", "CLTA3", "CGTV0", "CGTV1", "CGTV2", "CGTV3", "CGTA0", "CGTA1", "CGTA2", "CGTA3", "JMPA", "JMPD", "CALA", "CALD", "RET", "JPCA", "JPCD", "CLCA", "CLCD", "RETC", "BRK", "HLT", "DBGR0", "DBGR1", "DBGR2", "DBGR3", "DBGV", "DBGA", "DBCA", "DBCV", "DBCR0", "DBCR1", "DBCR2", "DBCR3", "ADOR0", "ADOR1", "ADOR2", "ADOR3", "ADOV", "ADOA", "INCD", "DECD", "IDIS", "IEN", "AOR", "Unused", "Unused", "Unused", "Unused", "Unused"};
const int InstructionDebuggingNumArgs[0x100] {0, 2, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

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
		callPendingInterrupt();
}

void cpu::debug() {
	unsigned short instr = MEMORY[PC];
	// if (PC >= 0x100 || instr == 0xd0)
	// 	return;
	std::stringstream output;
	output << "CPU INSTRUCTION $" << std::hex << std::setw(4) << std::setfill('0') << PC;
	if (instr < 0x100) {
		output << ":" << std::setw(2) << std::setfill('0') << instr;
		output << " (" << std::setw(5) << std::setfill(' ') << InstructionDebugging[instr];
		for (int i = 0; i < 2; i++) {
			if (i < InstructionDebuggingNumArgs[instr]) {
				output << ":" << std::hex << std::setw(4) << std::setfill('0') << MEMORY[PC+i+1];
			} else {
				output << "     ";
			}
		}
		output << ")" ;
	} else {
		output << ":" << std::setw(4) << std::setfill('0') << instr;
		output << " (ERR          )" ;
	}
	output << " | " << std::setw(4) << std::setfill('0') << R0;
	output << " | " << std::setw(4) << std::setfill('0') << R1;
	output << " | " << std::setw(4) << std::setfill('0') << R2;
	output << " | " << std::setw(4) << std::setfill('0') << R3;
	output << " | Stack[" << MEMORY[StackMemory] << "]: ";
	if (MEMORY[StackMemory] > 0xfff) {
		output << " !!!!";
	} else {
		for (int i = 1; i <= MEMORY[StackMemory]; i++) {
			output << " " << std::setw(4) << std::setfill('0') << MEMORY[StackMemory+i];
		}
	}
	std::string outputString = output.str();
	if (previousDebug != outputString) {
		std::cout << outputString << std::endl;
		previousDebug = outputString;
	}
	// std::cout << "VideoMode " << MEMORY[VideoSettings] << std::endl;
	// std::cout << "Jump " << jump << std::endl;
}

void cpu::readRegisterState(unsigned short Registers[]) {
	Registers[0] = PC;
	Registers[1] = R0;
	Registers[2] = R1;
	Registers[3] = R2;
	Registers[4] = R3;
	Registers[5] = DD;
	Registers[6] = offsetRegister;
	Registers[7] = MEMORY[StackMemory];
	Registers[8] = MEMORY[StackMemory + MEMORY[StackMemory]];
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
			if (!halted && !broken)
				std::cout << "ERR: Invalid display mode (" << displayMode << ") selected." << std::endl;
			color = 0;
			halted = true;
	}
	return color;
}

unsigned short cpu::getAtAddress(unsigned short address) {
	return MEMORY[address + offsetRegister];
}
unsigned short cpu::getArgument() {
	return MEMORY[++PC];
}
void cpu::setValueAtAddress(unsigned short value, unsigned short address) {
	MEMORY[address + offsetRegister] = value;
}
void cpu::pushToStack(unsigned short value) {
	unsigned short addr = ++MEMORY[StackMemory];
	MEMORY[StackMemory + addr] = value;
	if (MEMORY[StackMemory] == 0x1000) {
		std::cout << "ERR: Stack Overflow. Pushed to stack and pointer reached 0x1000" << std::endl;
		halted = true;
	}
}
unsigned short cpu::popFromStack() {
	unsigned short addr = MEMORY[StackMemory]--;
	if (MEMORY[StackMemory] == 0xffff) {
		std::cout << "ERR: Stack Underflow. Popped from stack and pointer under flowed to 0xffff" << std::endl;
		halted = true;
	}
	return MEMORY[StackMemory + addr];
}

void cpu::callInterrupt(unsigned short interrupt) {
	if (halted || broken)
		return;
	if (!interuptHandling) {
		std::cout << "WRN: Interrupt blocked" << std::endl;
		return;
	}
	if (interrupt > 0x5f) {
		std::cout << "ERR: Invalid interrupt 0x" << std::hex << std::setw(2) << std::setfill('0') << value << std::endl;
		halted = true;
		return;
	}
	interruptToCall = interrupt;
	needToInterrupt = true;
}

void cpu::ROMdump() {
	std::string romDumpName = "dump" + std::to_string(dumpFileNumber++) + ".hex";
	std::cout << "CPU ROMDUMP: ROM " << romDumpName << std::endl;
	std::ofstream hexFile;
	hexFile.open(romDumpName);
	int byteToWrite;
	if (hexFile.is_open()) {
		for (int i = 0; i < 0x10000; i++) {
			byteToWrite = MEMORY[i];
			hexFile << "0x" << std::hex << std::setw(4) << std::setfill('0') << byteToWrite << " ";
			if (i % 16 == 15) {
				hexFile << "\n";
			}
		}
	} else {
		std::cout << "File not open?" << std::endl;
	}
}

void cpu::callPendingInterrupt() {
	if (MEMORY[InterruptTableStart + interruptToCall] != 0) {
		pushToStack(PC-1);
		if (interruptToCall == 0x00) {
			// pushToStack(R0);
			// pushToStack(R1);
			// pushToStack(R2);
			// pushToStack(R3);
			for (int i = 0; i < PendingDataSize; i++) {
				MEMORY[IODataStart+i] = PendingIOData[i];
			}
			// std::cout << "Stacked " << (int)intArg0 << " and then " << (int)intArg1 << "!" << std::endl;
		}
		PC = MEMORY[InterruptTableStart + interruptToCall];
		needToInterrupt = false;
		PendingDataSize = 0;
	}
}

void cpu::keyStateChange(unsigned char keyCode, bool state) {
	PendingIOData[0] = state;
	PendingIOData[1] = keyCode;
	PendingDataSize = 2;
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

// The function below is automatically regenerated by the script mentioned above as well. The next two lines are searched for, through to the default condition
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
		R0 = ~R0;
		break;
	case 0x61: // NOT1
		R1 = ~R1;
		break;
	case 0x62: // NOT2
		R2 = ~R2;
		break;
	case 0x63: // NOT3
		R3 = ~R3;
		break;
	case 0x64: // NEG0
		R0 = -R0;
		break;
	case 0x65: // NEG1
		R1 = -R1;
		break;
	case 0x66: // NEG2
		R2 = -R2;
		break;
	case 0x67: // NEG3
		R3 = -R3;
		break;
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
	case 0x9c: // LDZ0
		R0 = R0;
		break;
	case 0x9d: // LDZ1
		R0 = R1;
		break;
	case 0x9e: // LDZ2
		R0 = R2;
		break;
	case 0x9f: // LDZ3
		R0 = R3;
		break;
	case 0xa0: // STZ0
		R0 = R0;
		break;
	case 0xa1: // STZ1
		R1 = R0;
		break;
	case 0xa2: // STZ2
		R2 = R0;
		break;
	case 0xa3: // STZ3
		R3 = R0;
		break;
	case 0xa4: // PSHR0
		pushToStack(R0);
		break;
	case 0xa5: // PSHR1
		pushToStack(R1);
		break;
	case 0xa6: // PSHR2
		pushToStack(R2);
		break;
	case 0xa7: // PSHR3
		pushToStack(R3);
		break;
	case 0xa8: // POPR0
		R0 = popFromStack();
		break;
	case 0xa9: // POPR1
		R1 = popFromStack();
		break;
	case 0xaa: // POPR2
		R2 = popFromStack();
		break;
	case 0xab: // POPR3
		R3 = popFromStack();
		break;
	case 0xac: // PSHA
		pushToStack(R0);
		pushToStack(R1);
		pushToStack(R2);
		pushToStack(R3);
		break;
	case 0xad: // POPA
		R3 = popFromStack();
		R2 = popFromStack();
		R1 = popFromStack();
		R0 = popFromStack();
		break;
	case 0xae: // CEZA
		jump = getAtAddress(getArgument()) == 0;
		break;
	case 0xaf: // CNZA
		jump = getAtAddress(getArgument()) != 0;
		break;
	case 0xb0: // CEZR0
		jump = R0 == 0;
		break;
	case 0xb1: // CEZR1
		jump = R1 == 0;
		break;
	case 0xb2: // CEZR2
		jump = R2 == 0;
		break;
	case 0xb3: // CEZR3
		jump = R3 == 0;
		break;
	case 0xb4: // CNZR0
		jump = R0 != 0;
		break;
	case 0xb5: // CNZR1
		jump = R1 != 0;
		break;
	case 0xb6: // CNZR2
		jump = R2 != 0;
		break;
	case 0xb7: // CNZR3
		jump = R3 != 0;
		break;
	case 0xb8: // CEV0
		jump = R0 == getArgument();
		break;
	case 0xb9: // CEV1
		jump = R1 == getArgument();
		break;
	case 0xba: // CEV2
		jump = R2 == getArgument();
		break;
	case 0xbb: // CEV3
		jump = R3 == getArgument();
		break;
	case 0xbc: // CEA0
		jump = R0 == getAtAddress(getArgument());
		break;
	case 0xbd: // CEA1
		jump = R1 == getAtAddress(getArgument());
		break;
	case 0xbe: // CEA2
		jump = R2 == getAtAddress(getArgument());
		break;
	case 0xbf: // CEA3
		jump = R3 == getAtAddress(getArgument());
		break;
	case 0xc0: // CNV0
		jump = R0 != getArgument();
		break;
	case 0xc1: // CNV1
		jump = R1 != getArgument();
		break;
	case 0xc2: // CNV2
		jump = R2 != getArgument();
		break;
	case 0xc3: // CNV3
		jump = R3 != getArgument();
		break;
	case 0xc4: // CNA0
		jump = R0 != getAtAddress(getArgument());
		break;
	case 0xc5: // CNA1
		jump = R1 != getAtAddress(getArgument());
		break;
	case 0xc6: // CNA2
		jump = R2 != getAtAddress(getArgument());
		break;
	case 0xc7: // CNA3
		jump = R3 != getAtAddress(getArgument());
		break;
	case 0xc8: // CLTV0
		jump = R0 < getArgument();
		break;
	case 0xc9: // CLTV1
		jump = R1 < getArgument();
		break;
	case 0xca: // CLTV2
		jump = R2 < getArgument();
		break;
	case 0xcb: // CLTV3
		jump = R3 < getArgument();
		break;
	case 0xcc: // CLTA0
		jump = R0 < getAtAddress(getArgument());
		break;
	case 0xcd: // CLTA1
		jump = R1 < getAtAddress(getArgument());
		break;
	case 0xce: // CLTA2
		jump = R2 < getAtAddress(getArgument());
		break;
	case 0xcf: // CLTA3
		jump = R3 < getAtAddress(getArgument());
		break;
	case 0xd0: // CGTV0
		jump = R0 > getArgument();
		break;
	case 0xd1: // CGTV1
		jump = R1 > getArgument();
		break;
	case 0xd2: // CGTV2
		jump = R2 > getArgument();
		break;
	case 0xd3: // CGTV3
		jump = R3 > getArgument();
		break;
	case 0xd4: // CGTA0
		jump = R0 > getAtAddress(getArgument());
		break;
	case 0xd5: // CGTA1
		jump = R1 > getAtAddress(getArgument());
		break;
	case 0xd6: // CGTA2
		jump = R2 > getAtAddress(getArgument());
		break;
	case 0xd7: // CGTA3
		jump = R3 > getAtAddress(getArgument());
		break;
	case 0xd8: // JMPA
		PC = getArgument()-1+offsetRegister;
		break;
	case 0xd9: // JMPD
		PC = DD-1+offsetRegister;
		break;
	case 0xda: // CALA
		pushToStack(PC+1-offsetRegister);
		PC = getArgument()-1+offsetRegister;
		break;
	case 0xdb: // CALD
		pushToStack(PC-offsetRegister);
		PC = DD-1+offsetRegister;
		break;
	case 0xdc: // RET
		PC = popFromStack()+offsetRegister;
		break;
	case 0xdd: // JPCA
		value = getArgument();
		if(jump)
			PC = value-1+offsetRegister;
		break;
	case 0xde: // JPCD
		if(jump)
			PC = DD-1+offsetRegister;
		break;
	case 0xdf: // CLCA
		value = getArgument();
		if(jump) {
			pushToStack(PC);
			PC = value-1+offsetRegister;
		}
		break;
	case 0xe0: // CLCD
		if(jump) {
			pushToStack(PC);
			PC = DD-1+offsetRegister;
		}
		break;
	case 0xe1: // RETC
		if(jump)
			PC = popFromStack()+offsetRegister;
		break;
	case 0xe2: // BRK
		std::cout << "\nCPU BREAK" << std::endl;
		broken = true;
		break;
	case 0xe3: // HLT
		std::cout << "\nCPU HALT" << std::endl;
		halted = true;
		break;
	case 0xe4: // DBGR0
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R0 << std::endl;
		break;
	case 0xe5: // DBGR1
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R1 << std::endl;
		break;
	case 0xe6: // DBGR2
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R2 << std::endl;
		break;
	case 0xe7: // DBGR3
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << R3 << std::endl;
		break;
	case 0xe8: // DBGV
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << getArgument() << std::endl;
		break;
	case 0xe9: // DBGA
		std::cout << "0x" << std::hex << std::setw(4) << std::setfill('0') << getAtAddress(getArgument()) << std::endl;
		break;
	case 0xea: // DBCA
		value = getAtAddress(getArgument());
		if (value != '\n') 
			std::cout << (char)value;
		else if (flushDebugChar || value == '\n')
			std::cout << std::endl;
		break;
	case 0xeb: // DBCV
		value = getArgument();
		if (value != '\n') 
			std::cout << (char)value;
		else if (flushDebugChar || value == '\n')
			std::cout << std::endl;
		break;
	case 0xec: // DBCR0
		value = R0;
		if (value != '\n') 
			std::cout << (char)value;
		else if (flushDebugChar || value == '\n')
			std::cout << std::endl;
		break;
	case 0xed: // DBCR1
		value = R1;
		if (value != '\n') 
			std::cout << (char)value;
		else if (flushDebugChar || value == '\n')
			std::cout << std::endl;
		break;
	case 0xee: // DBCR2
		value = R2;
		if (value != '\n') 
			std::cout << (char)value;
		else if (flushDebugChar || value == '\n')
			std::cout << std::endl;
		break;
	case 0xef: // DBCR3
		value = R3;
		if (value != '\n') 
			std::cout << (char)value;
		else if (flushDebugChar || value == '\n')
			std::cout << std::endl;
		break;
	case 0xf0: // ADOR0
		offsetRegister = R0;
		break;
	case 0xf1: // ADOR1
		offsetRegister = R1;
		break;
	case 0xf2: // ADOR2
		offsetRegister = R2;
		break;
	case 0xf3: // ADOR3
		offsetRegister = R3;
		break;
	case 0xf4: // ADOV
		offsetRegister = getArgument();
		break;
	case 0xf5: // ADOA
		offsetRegister = getAtAddress(getArgument());
		break;
	case 0xf6: // INCD
		DD++;
		break;
	case 0xf7: // DECD
		DD--;
		break;
	case 0xf8: // IDIS
		interuptHandling = false;
		break;
	case 0xf9: // IEN
		interuptHandling = true;
		break;
	case 0xfa: // AOR
		R0 = offsetRegister;
		break;
	// case 0xfb:
	// case 0xfc:
	// case 0xfd:
	// case 0xfe:
	// case 0xff:
	default:
		std::cout << "Unknown Instruction: " << instruction << "(PC:0x" << std::hex << std::setw(4) << std::setfill('0') << PC << ")" << std::endl;
		halted = true;
	}
}