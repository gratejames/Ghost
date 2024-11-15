#include <iostream>
#include <vector>
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

private:
	std::string romFileName;
	int t = 0; 							// Instructions since last reset
	unsigned short PC = 0; 				// Program Counter: Address of current instruction
	unsigned short DD = 0; 				// Address Register
	unsigned short R0 = 0;
	unsigned short R1 = 0;
	unsigned short R2 = 0;
	unsigned short R3 = 0;
	unsigned short value = 0;			// Used in instruction logic
	unsigned short instruction = 0;		// ^
	unsigned short offsetRegister = 0;
	bool jump = false;

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