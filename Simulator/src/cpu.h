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

	bool halted;
	bool broken;
	bool closed;

	bool verbose;
	bool flushDebugChar;

private:
	std::string romFileName;
	int t; 							// Instructions since last reset
	unsigned short MEMORY[0x10000];
	unsigned short PC; 				// Program Counter: Address of current instruction
	unsigned short DD; 				// Address Register
	unsigned short R0;
	unsigned short R1;
	unsigned short R2;
	unsigned short R3;
	unsigned short value;			// Used in instruction logic
	unsigned short instruction;		// ^
	unsigned short offsetRegister;
	bool jump;

	unsigned short getAtAddress(unsigned short address);
	unsigned short getArgument();
	void setValueAtAddress(unsigned short value, unsigned short address);
	void pushToStack(unsigned short);
	unsigned short popFromStack();
	void executeFunction(unsigned short instruction);

	void callPendingInterrupt(); // From ticker thread, jumps
	void callInterrupt(unsigned short interrupt); // From event thread, queues
	unsigned short interruptToCall;
	bool needToInterrupt;

	// Color conversions
	int rgb565_888(unsigned short x);
	int drgb_888(unsigned short x);
	int pallette16_888(unsigned short x);
	int pallette2_888(unsigned short x);
};