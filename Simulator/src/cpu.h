#include <iostream>
#include <stdio.h>

class cpu {
public:
	cpu(std::string romFile);
	void tick();
	void reset();
	void debug();
	int getColorAt(int x);

	void bootloader();

	void keyStateChange(unsigned char keyCode, bool state);

	void memLog(unsigned short from, unsigned short to);

	bool halted = false;
	bool broken = false;
	bool closed = false;

	bool verbose = false;
	bool flushDebugChar = false;
	unsigned short MEMORY[0x10000] = {};
	struct Instruction;
	void readRegisterState(unsigned short registers[]);
	void readCurrentInstruction(Instruction &inst);
	void ROMdump();

private:
	std::string romFileName;
	int t = 0; 							// Instructions since last reset
	unsigned short PC = 0; 				// Program Counter: Address of current instruction
	unsigned short DD = 0; 				// Address Register
	unsigned short R0 = 0;
	unsigned short R1 = 0;
	unsigned short R2 = 0;
	unsigned short R3 = 0;
	unsigned short SP = 0;
	unsigned short value = 0;			// Used in instruction logic
	unsigned short instruction = 0;		// ^
	unsigned short offsetRegister = 0;
	bool jump = false;

	int dumpFileNumber = 0;

	std::string previousDebug;
	unsigned short PendingIOData[8] = {};
	int PendingDataSize = 0;
	bool interuptHandling = true;
	const std::set <unsigned short> AllowedInterrupts {
		0x00, // HACK

		0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f,
		0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f,
	};

	unsigned short getAtAddress(unsigned short address);
	unsigned short getArgument();
	void setValueAtAddress(unsigned short value, unsigned short address);
	void pushToStack(unsigned short);
	unsigned short popFromStack();
	void executeFunction(unsigned short instruction);

	void callPendingInterrupt(); // From ticker thread, jumps
	void callInterrupt(unsigned short interrupt); // From event thread, queues
	unsigned short interruptToCall = 0;
	bool needToInterrupt = false;

	// Color conversions
	int rgb565_888(unsigned short x);
	int drgb_888(unsigned short x);
	int pallette16_888(unsigned short x);
	int pallette2_888(unsigned short x);
};

struct cpu::Instruction {
	unsigned short opcode;
	int args;
	std::string name;
};
