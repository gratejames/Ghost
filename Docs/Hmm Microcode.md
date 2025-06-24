
| Instruction  | Hex  | Description                                       | Action                              | Mnem | Shrt  | Arguments         | Microcode                                                                                                             | Test |
| ------------ | ---- | ------------------------------------------------- | ----------------------------------- | ---- | ----- | ----------------- | --------------------------------------------------------------------------------------------------------------------- | ---- |
| Basic        |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| 0b00000000   | 0x00 | No Operation                                      | Setup MC for next instruction       | NOP  |       | None              | PC->MA,PC++,MD->MPC                                                                                                   | T0 P |
| 0b00000001   | 0x01 | Move between two addresses                        | Address → Address                   | MVAA | MV    | Address, Address  | PC->MA,PC++,MD->MA,MD->VR,PC->MA,PC++,MD->MA,VR->MW,X                                                                 | T0 P |
| 0b00000010   | 0x02 | Load value into AddressRegister                   | Value → AddressRegister             | DDV  | DD    | Value             | PC->MA,PC++,MD->AR,X                                                                                                  | T0 P |
| 0b00000011   | 0x03 | Load address into AddressRegister                 | Address → AddressRegister           | DDA  | DD    | Address           | PC->MA,PC++,MD->MA,MD->AR,X                                                                                           | T0 P |
| 0b000001RR   | 0x04 | Load register into AddressRegister                | Register → AddressRegister          | DDR  | DD    | Register          | RR->AR,X                                                                                                              | T0 P |
| 0b000010RR   | 0x08 | Load value into register                          | Value → Register                    | LDV  | LD    | Register, Value   | PC->MA,PC++,MD->RR,X                                                                                                  | T0 P |
| 0b000011RR   | 0x0c | Load from address into register                   | Address → Register                  | LDA  | LD    | Register, Address | PC->MA,PC++,MD->MA,MD->RR,X                                                                                           | T0 P |
| 0b000100RR   | 0x10 | Load from at AddressRegister into Register        | $AddressRegister → Register         | LDD  | LD    | Register          | AR->MA,MD->RR,X                                                                                                       | T0 P |
| 0b000101RR   | 0x14 | Store register at address                         | Register → Address                  | STR  | ST    | Register, Address | PC->MA,PC++,MD->MA,RR->MW,X                                                                                           | T0 P |
| 0b000110RR   | 0x18 | Store value at register                           | Value → $Register                   | STAR | ST    | Register, Value   | PC->MA,PC++,MD->VR,RR->MA,VR->MW,X                                                                                    | T2 P |
| 0b00011100   | 0x1c | Store value into address                          | Value → Address                     | STV  | ST    | Value, Address    | PC->MA,PC++,MD->VR,PC->MA,PC++,MD->MA,VR->MW,X                                                                        | T0 P |
| 0b00011101   | 0x1d | Store value at AddressRegister                    | Value → $AddressRegister            | STDV | STD   | Value             | PC->MA,PC++,MD->VR,AR->MA,VR->MW,X                                                                                    | T0 P |
| 0b00011110   | 0x1e | Move from at AddressRegister to at Address        | AddressRegister → Address           | MVDD | MV    | Address           | AR->MA,MD->VR,PC->MA,PC++,MD->MA,VR->MW,X                                                                             |      |
| 0b00011111   | 0x1f | Call Interrupt at Value                           | Interrupt Value                     | INT  |       | Value             |                                                                                                                       |      |
| 0b001000RR   | 0x20 | Store register at AddressRegister                 | Register → $AddressRegister         | STDR | STD   | Register          | AR->MA,RR->MW,X                                                                                                       | T0 P |
|              |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| Math         |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| 0b001001RR   | 0x24 | SHL Register by value                             | Register << Value                   | SHLV | SHL   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math0100,Y->RR,X                                                                              | T3 P |
| 0b001010RR   | 0x28 | SHL Register by address                           | Register << Address                 | SHLA | SHL   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math0100,Y->RR,X                                                                       | T3 P |
| 0b001011RR   | 0x2c | SHL R0 by register                                | R0 << Register                      | SHLR | SHL   | Register          | R0->A,RR->B,Math0100,Y->R0,X                                                                                          | T3 P |
| 0b001100RR   | 0x30 | SHR Register by value                             | Register >> Value                   | SHRV | SHR   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math0101,Y->RR,X                                                                              | T3 P |
| 0b001101RR   | 0x34 | SHR Register by address                           | Register >> Address                 | SHRA | SHR   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math0101,Y->RR,X                                                                       | T3 P |
| 0b001110RR   | 0x38 | SHR R0 by register                                | R0 >> Register                      | SHRR | SHR   | Register          | R0->A,RR->B,Math0101,Y->R0,X                                                                                          | T3 P |
| 0b001111RR   | 0x3c | Add value to register                             | Register += Value                   | ADDV | ADD   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math0000,Y->RR,X                                                                              | T3 P |
| 0b010000RR   | 0x40 | Add address to register                           | Register += Address                 | ADDA | ADD   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math0000,Y->RR,X                                                                       | T3 P |
| 0b010001RR   | 0x44 | Add register to R0                                | R0 += Register                      | ADDR | ADD   | Register          | R0->A,RR->B,Math0000,Y->R0,X                                                                                          | T3 P |
| 0b010010RR   | 0x48 | Subtract value from register                      | Register -= Value                   | SUBV | SUB   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math0001,Y->RR,X                                                                              | T3 P |
| 0b010011RR   | 0x4c | Subtract address from register                    | Register -= Address                 | SUBA | SUB   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math0001,Y->RR,X                                                                       | T3 P |
| 0b010100RR   | 0x50 | Subtract register from R0                         | R0 -= Register                      | SUBR | SUB   | Register          | R0->A,RR->B,Math0001,Y->R0,X                                                                                          | T3 P |
| 0b010101RR   | 0x54 | Subtract register from value, store to register   | Value - Register → Register         | SBRV | SBR   | Register, Value   | RR->B,PC->MA,PC++,MD->A,Math0001,Y->RR,X                                                                              | T3 P |
| 0b010110RR   | 0x58 | Subtract register from address, store to register | Address - Register → Register       | SBRA | SBR   | Register, Address | RR->B,PC->MA,PC++,MD->MA,MD->A,Math0001,Y->RR,X                                                                       | T3 P |
| 0b010111RR   | 0x5c | Subtract R0 from register, store to R0            | R0 = Register - R0                  | SBRR | SBR   | Register          | R0->B,RR->A,Math0001,Y->R0,X                                                                                          | T3 P |
| 0b011000RR   | 0x60 | NOT Register                                      | NOT                                 | NOT  |       | Register          | RR->A,Math1011,Y->RR,X                                                                                                | T3 P |
| 0b01100100   | 0x64 | Push all registers to stack                       | Push All                            | PSHA | PSH   | None              | SP->MA,MD->A,Math0010,Y->A,SP->B,Math0000,Y->MA,R0->MW,   Y->A,Math0010,Y->MA,R1->MW,   Y->A,Math0010,Y->MA,R2->MW,   | T2 P |
| 0b01100101   | 0x65 | Push cont...                                      | Push cont...                        |      |       |                   | Y->A,Math0010,Y->MA,R3->MW,   Y->A,SP->B,Math0001,SP->MA,Y->MW,X                                                      | -    |
| 0b01100110   | 0x66 | Pop all registers from stack                      | Pop All                             | POPA | POP   | None              | SP->MA,MD->A,SP->B,Math0000,Y->MA,MD->R3,   Y->A,Math0011,Y->MA,MD->R2,   Y->A,Math0011,Y->MA,MD->R1,   Y->A,Math0011 | T2 P |
| 0b01100111   | 0x67 | Pop cont...                                       | Pop cont...                         |      |       |                   | Y->MA,MD->R0,   Y->A,Math0011,Y->A,SP->B,Math0001,SP->MA,Y->MW,X                                                      | -    |
| 0b011010RR   | 0x68 | Increase Register                                 | Increase                            | INC  |       | Register          | RR->A,Math0010,Y->RR,X                                                                                                | T0 P |
| 0b011011RR   | 0x6c | Decrease Register                                 | Decrease                            | DEC  |       | Register          | RR->A,Math0011,Y->RR,X                                                                                                | T3 P |
| 0b011100RR   | 0x70 | Shift Register Left 1                             | Register << 1                       | SHLO |       | Register          | RR->A,Math0110,Y->RR,X                                                                                                | T3 P |
| 0b011101RR   | 0x74 | Shift Register Right 1                            | Register >> 1                       | SHRO |       | Register          | RR->A,Math0111,Y->RR,X                                                                                                | T3 P |
| 0b011110RR   | 0x78 | Register AND Value                                | Register AND Value                  | ANDV | AND   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math1000,Y->RR,X                                                                              | T3 P |
| 0b011111RR   | 0x7c | Register AND Address                              | Register AND Address                | ANDA | AND   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math1000,Y->RR,X                                                                       | T3 P |
| 0b100000RR   | 0x80 | Register AND Address                              | R0 = Register AND R0                | ANDR | AND   | Register          | R0->A,RR->B,Math1000,Y->R0,X                                                                                          | T3 P |
| 0b100001RR   | 0x84 | Register OR Value                                 | Register OR Value                   | ORV  | OR    | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math1001,Y->RR,X                                                                              | T3 P |
| 0b100010RR   | 0x88 | Register OR Address                               | Register OR Address                 | ORA  | OR    | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math1001,Y->RR,X                                                                       | T3 P |
| 0b100011RR   | 0x8c | Register OR Address                               | R0 = Register OR R0                 | ORR  | OR    | Register          | R0->A,RR->B,Math1001,Y->R0,X                                                                                          | T3 P |
| 0b100100RR   | 0x90 | Register XOR Value                                | Register XOR Value                  | XORV | XOR   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math1010,Y->RR,X                                                                              | T3 P |
| 0b100101RR   | 0x94 | Register XOR Address                              | Register XOR Address                | XORA | XOR   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math1010,Y->RR,X                                                                       | T3 P |
| 0b100110RR   | 0x98 | Register XOR Address                              | R0 = Register XOR R0                | XORR | XOR   | Register          | R0->A,RR->B,Math1010,Y->R0,X                                                                                          | T3 P |
| 0b100111RR   | 0x9c | From RR to R0                                     | R0 = RR                             | LDZ  |       | Register          | RR->R0,X                                                                                                              | T3 P |
| 0b101000RR   | 0xa0 | From R0 to RR                                     | RR = R0                             | STZ  |       | Register          | R0->RR,X                                                                                                              | T3 P |
|              |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| Stack        |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| 0b101001RR   | 0xa4 | Push Register to stack                            | Push Register                       | PSHR | PSH   | Register          | SP->MA,MD->A,Math0010,Y->MW,Y->A,SP->B,Math0000,Y->MA,RR->MW,X                                                        | T2 P |
| 0b101010RR   | 0xa8 | Pop register to stack                             | Pop Register                        | POPR | POP   | Register          | SP->MA,MD->A,Math0011,Y->MW,SP->B,Math0000,Y->MA,MD->RR,X                                                             | T2 P |
| 0b10101100   | 0xac | Stack pointer to R0                               | R0 = SP                             | LDSP |       | None              |                                                                                                                       |      |
| 0b10101101   | 0xad | R0 to stack pointer                               | SP = R0                             | STSP |       | None              |                                                                                                                       |      |
|              |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| Conditionals |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| 0b10101110   | 0xae |                                                   | Cond Address=0                      | CEZA | CEZ   | Address           | PC->MA,PC++,MD->MA,MD->A,Other1000,Math1100,X                                                                         | T1 P |
| 0b10101111   | 0xaf |                                                   | Cond Address!=0                     | CNZA | CNZ   | Address           | PC->MA,PC++,MD->MA,MD->A,Other1000,Math1101,X                                                                         | T1 P |
| 0b101100RR   | 0xb0 |                                                   | Cond Register=0                     | CEZR | CEZ   | Register          | RR->A,Other1000,Math1100,X                                                                                            | T1 P |
| 0b101101RR   | 0xb4 |                                                   | Cond Register!=0                    | CNZR | CNZ   | Register          | RR->A,Other1000,Math1101,X                                                                                            | T1 P |
| 0b101110RR   | 0xb8 |                                                   | Cond Register=Value                 | CEV  | CE    | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math1100,X                                                                                    | T1 P |
| 0b101111RR   | 0xbc |                                                   | Cond Register=Address               | CEA  | CE    | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math1100,X                                                                             | T1 P |
| 0b110000RR   | 0xc0 |                                                   | Cond Register!=Value                | CNV  | CNE   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math1101,X                                                                                    | T1 P |
| 0b110001RR   | 0xc4 |                                                   | Cond Register!=Address              | CNA  | CNE   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math1101,X                                                                             | T1 P |
| 0b110010RR   | 0xc8 |                                                   | Cond Register<Value                 | CLTV | CLT   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math1110,X                                                                                    | T1 P |
| 0b110011RR   | 0xcc |                                                   | Cond Register<Address               | CLTA | CLT   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math1110,X                                                                             | T1 P |
| 0b110100RR   | 0xd0 |                                                   | Cond Register>Value                 | CGTV | CGT   | Register, Value   | PC->MA,PC++,RR->A,MD->B,Math1111,X                                                                                    | T1 P |
| 0b110101RR   | 0xd4 |                                                   | Cond Register>Address               | CGTA | CGT   | Register, Address | PC->MA,PC++,RR->A,MD->MA,MD->B,Math1111,X                                                                             | T1 P |
|              |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| Control Flow |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| 0b11011000   | 0xd8 |                                                   | Jump Address                        | JMPA | JMP   | Value             | PC->MA,MD->PC,X                                                                                                       | T1 P |
| 0b11011001   | 0xd9 |                                                   | Jump AddressRegister                | JMPD | JMP   | None              | AR->PC,X                                                                                                              | T1 P |
| 0b11011010   | 0xda |                                                   | Routine Address                     | CALA | CALL  | Value             | PC->MA,MD->VR,SP->MA,MD->A,Math0010,Y->MW,Y->A,SP->B,Math0000,Y->MA,PC->A,Math0010,Y->MW,VR->PC,X                     |      |
| 0b11011011   | 0xdb |                                                   | Routine AddressRegister             | CALD | CALL  | None              | SP->MA,MD->A,Math0010,Y->MW,Y->A,SP->B,Math0000,Y->MA,PC->MW,AR->PC,X                                                 |      |
| 0b11011100   | 0xdc |                                                   | Return                              | RET  |       | None              | SP->MA,MD->A,Math0011,Y->MW,SP->B,Math0000,Y->MA,MD->PC,X                                                             |      |
| 0b11011101   | 0xdd |                                                   | Jump Conditional Address            | JPCA | JMPC  | Value             | PC->MA,PC++,XIC,MD->PC,X                                                                                              | T1 P |
| 0b11011110   | 0xde |                                                   | Jump Conditional AddressRegister    | JPCD | JMPC  | None              | XIC,AR->PC,X                                                                                                          | T1 P |
| 11011111     | 0xdf |                                                   | Routine Conditional Address         | CLCA | CALLC | Value             | PC->MA,PC++,XIC,MD->VR,SP->MA,MD->A,Math0010,Y->MW,Y->A,SP->B,Math0000,Y->MA,PC->A,Math0010,Y->MW,VR->PC,X            |      |
| 0b11100000   | 0xe0 |                                                   | Routine Conditional AddressRegister | CLCD | CALLC | None              | XIC,SP->MA,MD->A,Math0010,Y->MW,Y->A,SP->B,Math0000,Y->MA,PC->MW,AR->PC,X                                             |      |
| 0b11100001   | 0xe1 |                                                   | Return Conditional                  | RETC |       | None              | XIC,SP->MA,MD->A,Math0011,Y->MW,SP->B,Math0000,Y->MA,MD->PC,X                                                         |      |
| 0b11100010   | 0xe2 |                                                   | Break                               | BRK  |       | None              | Halt,X                                                                                                                |      |
| 0b11100011   | 0xe3 |                                                   | Halt                                | HLT  |       | None              | Halt,X                                                                                                                | T0 P |
|              |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| Extended     |      |                                                   |                                     |      |       |                   |                                                                                                                       |      |
| 0b111001RR   | 0xe4 | Send register to the debugging terminal           | Register → DBG                      | DBGR | DBG   | Register          | RR->DBG,X                                                                                                             | T1 P |
| 0b11101000   | 0xe8 | Output value to the debugging terminal            | Value → DBG                         | DBGV | DBG   | Value             | PC->MA,PC++,MD->DBG,X                                                                                                 | T2 P |
| 0b11101001   | 0xe9 | Output address to the debugging terminal          | Address → DBG                       | DBGA | DBG   | Address           | PC->MA,PC++,MD->MA,MD->DBG,X                                                                                          | T2 P |
| 0b11101010   | 0xea | Output address to the debugging terminal as char  | Address → DBG (Char)                | DBCA | DBGC  | Address           | PC->MA,PC++,MD->MA,MD->DBGC,X                                                                                         | T2 P |
| 0b11101011   | 0xeb | Output value to the debugging terminal as char    | Value → DBG (Char)                  | DBCV | DBGC  | Value             | PC->MA,PC++,MD->DBGC,X                                                                                                | T2 P |
| 0b111011RR   | 0xec | Send register to the debugging terminal as char   | Register → DBG (Char)               | DBCR | DBGC  | Register          | RR->DBGC,X                                                                                                            | T2 P |
| 0b111100RR   | 0xf0 | Load register to AddressOffset                    | Register → AddressOffset            | ADOR | ADO   | Register          | RR->AO,X                                                                                                              |      |
| 0b11110100   | 0xf4 | Load value to AddressOffset                       | Value → AddressOffset               | ADOV | ADO   | Value             | PC->MA,PC++,MD->AO,X                                                                                                  |      |
| 0b11110101   | 0xf5 | Load address to AddressOffset                     | Address → AddressOffset             | ADOA | ADO   | Address           | PC->MA,PC++,MD->MA,MD->AO,X                                                                                           |      |
| 0b11110110   | 0xf6 | Increment the addressRegister                     |                                     | INCD |       | None              | AR->A,Math0010,Y->AR,X                                                                                                | T2 P |
| 0b11110111   | 0xf7 | Decrement the addressRegister                     |                                     | DECD |       | None              | AR->A,Math0011,Y->AR,X                                                                                                | T2 P |
| 0b11111000   | 0xf8 | Disable Interrupts                                |                                     | IDIS |       | None              | Other0010,X                                                                                                           |      |
| 0b11111001   | 0xf9 | Enable Interrupts                                 |                                     | IEN  |       | None              | Other0001,X                                                                                                           |      |
| 0b11111010   | 0xfa | Copy the AO into R0                               |                                     | AOR  |       | None              | AO->R0,X                                                                                                              |      |
| 0b11111011   | 0xfb | Push the conditional to the stack                 |                                     | CPSH |       | None              | SP->MA,MD->A,Math0010,Y->MW,Y->A,SP->B,Math0000,Y->MA,Cond->MW,X                                                      | T2 P |
| 0b11111100   | 0xfc | Pop the conditional from the stack                |                                     | CPOP |       | None              | SP->MA,MD->A,Math0011,Y->MW,SP->B,Math0000,Y->MA,MD->A,Other1001,Math1100,X                                           | T2 P |


Microcode, First Nibble:

| Nibb | Action      |
| ---- | ----------- |
| 0000 | R0 out      |
| 0001 | R1 out      |
| 0010 | R2 out      |
| 0011 | R3 out      |
| 0100 | PC out      |
| 0101 | Value Out   |
| 0110 | Address out |
| 0111 | MDR out     |
| 1000 | Y out       |
| 1001 | AO out      |
| 1010 | SP out      |
| 1011 | Cond out    |
| 1100 |             |
| 1101 |             |
| 1110 | Math Nib    |
| 1111 | Other Nib   |

Microcode, Second Nibble:

| Nibb | Action     |
| ---- | ---------- |
| 0000 | R0 in      |
| 0001 | R1 in      |
| 0010 | R2 in      |
| 0011 | R3 in      |
| 0100 | PC in      |
| 0101 | Value in   |
| 0110 | Address in |
| 0111 | MWR in     |
| 1000 | MAR in     |
| 1001 | A in       |
| 1010 | B in       |
| 1011 | AO in      |
| 1100 | DBG in     |
| 1101 | DBGC in    |
| 1110 | MPC in     |
| 1111 | RP in      |

Microcode, Math Nibble:

| Nibb | Action |
| ---- | ------ |
| 0000 | ADD    |
| 0001 | SUB    |
| 0010 | INC    |
| 0011 | DEC    |
| 0100 | SHL    |
| 0101 | SHR    |
| 0110 | SHL 1  |
| 0111 | SHR 1  |
| 1000 | AND    |
| 1001 | OR     |
| 1010 | XOR    |
| 1011 | NOT    |
| 1100 | ==     |
| 1101 | !==    |
| 1110 | A<B    |
| 1111 | A>B    |

Microcode, Other Nibble:


| Nibb | Action                      |
| ---- | --------------------------- |
| 0000 |                             |
| 0001 | Enable INTs                 |
| 0010 | Disable INTs                |
| 0011 |                             |
| 0100 |                             |
| 0101 |                             |
| 0110 |                             |
| 0111 |                             |
| 1000 | 0x00 -> B                   |
| 1001 | 0xff -> B                   |
| 1010 |                             |
| 1011 |                             |
| 1100 | Done, inverse conditionally |
| 1101 | Done, conditionally         |
| 1110 | Halt                        |
| 1111 | Done                        |


Test Programs:
```
LD R0 3
ST R0 $val
MV $val $val+1
ST 0xaa $val
HLT
val:
.db 0
.db 0

Hand Assembled: (val = 0xb)
0x08 0x03
0x14 0x0b
0x01 0x0b 0x0c
0x1c 0xaa 0x0b
0xe3
0x00
0x00

```

```
LD R0 5
ADD R0 7
SUB R0 2
HLT

0x08 0x05
0x3c 0x07
0x48 0x02
0xe3
```