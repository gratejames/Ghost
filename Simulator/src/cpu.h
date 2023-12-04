#include <iostream>
#include <stdio.h>
#include <vector>

class cpu {
public:
	cpu(std::string romFile);
	void tick();
	void reset();
	void debug();
	int getColorAt(int x);

	bool halted;
	bool broken;

	bool closed;
	void bootloader();

	bool verbose;

private:
	int t; // Instructions since last reset
	unsigned short MEMORY[0x10000];

	std::string romFileName;

	unsigned short PC; // Program Counter: Address of current instruction
	unsigned short DD; // Address Register
	unsigned short R0;
	unsigned short R1;
	unsigned short R2;
	unsigned short R3;

	unsigned short value;

	unsigned short getAtAddress(unsigned short address);
	unsigned short getArgument();
	void setValueAtAddress(unsigned short value, unsigned short address);
	void pushToStack(unsigned short);
	unsigned short popFromStack();
	bool jump;

	unsigned short offsetRegister;

	void executeFunction(unsigned short instruction);
	unsigned short instruction;

	// Color conversions
	int rgb565_888(unsigned short x);
	int drgb_888(unsigned short x);
	int pallette16_888(unsigned short x);
	int pallette2_888(unsigned short x);
};