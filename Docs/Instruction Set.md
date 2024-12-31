
| Instruction  | Hex  | Description                                       | Action                              | Mnem | Shrt  | Arguments         | Status |
| ------------ | ---- | ------------------------------------------------- | ----------------------------------- | ---- | ----- | ----------------- | ------ |
| Basic        |      |                                                   |                                     |      |       |                   |        |
| 0b00000000   | 0x00 | No Operation                                      | No Operation                        | NOP  |       | None              | PASS   |
| 0b00000001   | 0x01 | Move between two addresses                        | Address → Address                   | MVAA | MV    | Address, Address  | PASS   |
| 0b00000010   | 0x02 | Load value into AddressRegister                   | Value → AddressRegister             | DDV  | DD    | Value             | PASS   |
| 0b00000011   | 0x03 | Load address into AddressRegister                 | Address → AddressRegister           | DDA  | DD    | Address           |        |
| 0b000001RR   | 0x04 | Load register into AddressRegister                | Register → AddressRegister          | DDR  | DD    | Register          |        |
| 0b000010RR   | 0x08 | Load value into register                          | Value → Register                    | LDV  | LD    | Register, Value   | PASS   |
| 0b000011RR   | 0x0c | Load from address into register                   | Address → Register                  | LDA  | LD    | Register, Address | PASS   |
| 0b000100RR   | 0x10 | Load from at AddressRegister into Register        | $AddressRegister → Register         | LDD  | LD    | Register          |        |
| 0b000101RR   | 0x14 | Store register at address                         | Register → Address                  | STR  | ST    | Register, Address |        |
| 0b000110RR   | 0x18 | Store value at register                           | Value → $Register                   | STAR | ST    | Register, Value   |        |
| 0b00011100   | 0x1c | Store value into address                          | Value → Address                     | STV  | ST    | Value, Address    | PASS   |
| 0b00011101   | 0x1d | Store value at AddressRegister                    | Value → $AddressRegister            | STDV | STD   | Value             |        |
| 0b00011110   | 0x1e | Move from at AddressRegister to at Address        | AddressRegister → Address           | MVDD | MV    | Address           |        |
| 0b00011111   | 0x1f | Call Interrupt at Value                           | Interrupt Value                     | INT  |       | Value             |        |
| 0b001000RR   | 0x20 | Store register at AddressRegister                 | Register → $AddressRegister         | STDR | STD   | Register          |        |
|              |      |                                                   |                                     |      |       |                   |        |
| Math         |      |                                                   |                                     |      |       |                   |        |
| 0b001001RR   | 0x24 | SHL Register by value                             | Register << Value                   | SHLV | SHL   | Register, Value   |        |
| 0b001010RR   | 0x28 | SHL Register by address                           | Register << Address                 | SHLA | SHL   | Register, Address |        |
| 0b001011RR   | 0x2c | SHL R0 by register                                | R0 << Register                      | SHLR | SHL   | Register          |        |
| 0b001100RR   | 0x30 | SHR Register by value                             | Register >> Value                   | SHRV | SHR   | Register, Value   |        |
| 0b001101RR   | 0x34 | SHR Register by address                           | Register >> Address                 | SHRA | SHR   | Register, Address |        |
| 0b001110RR   | 0x38 | SHR R0 by register                                | R0 >> Register                      | SHRR | SHR   | Register          |        |
| 0b001111RR   | 0x3c | Add value to register                             | Register += Value                   | ADDV | ADD   | Register, Value   |        |
| 0b010000RR   | 0x40 | Add address to register                           | Register += Address                 | ADDA | ADD   | Register, Address |        |
| 0b010001RR   | 0x44 | Add register to R0                                | R0 += Register                      | ADDR | ADD   | Register          |        |
| 0b010010RR   | 0x48 | Subtract value from register                      | Register -= Value                   | SUBV | SUB   | Register, Value   |        |
| 0b010011RR   | 0x4c | Subtract address from register                    | Register -= Address                 | SUBA | SUB   | Register, Address |        |
| 0b010100RR   | 0x50 | Subtract register from R0                         | R0 -= Register                      | SUBR | SUB   | Register          |        |
| 0b010101RR   | 0x54 | Subtract register from value, store to register   | Value - Register → Register         | SBRV | SBR   | Register, Value   |        |
| 0b010110RR   | 0x58 | Subtract register from address, store to register | Address - Register → Register       | SBRA | SBR   | Register, Address |        |
| 0b010111RR   | 0x5c | Subtract R0 from register, store to R0            | R0 = Register - R0                  | SBRR | SBR   | Register          |        |
| 0b011000RR   | 0x60 | NOT Register                                      | NOT                                 | NOT  |       | Register          |        |
| 0b011001RR   | 0x64 | Negate Register (Twos Compliment)                 | Negate                              | NEG  |       | Register          |        |
| 0b011010RR   | 0x68 | Increase Register                                 | Increase                            | INC  |       | Register          | PASS   |
| 0b011011RR   | 0x6c | Decrease Register                                 | Decrease                            | DEC  |       | Register          |        |
| 0b011100RR   | 0x70 | Shift Register Left 1                             | Register << 1                       | SHLO |       | Register          |        |
| 0b011101RR   | 0x74 | Shift Register Right 1                            | Register >> 1                       | SHRO |       | Register          |        |
| 0b011110RR   | 0x78 | Register AND Value                                | Register AND Value                  | ANDV | AND   | Register, Value   |        |
| 0b011111RR   | 0x7c | Register AND Address                              | Register AND Address                | ANDA | AND   | Register, Address |        |
| 0b100000RR   | 0x80 | Register AND Address                              | R0 = Register AND R0                | ANDR | AND   | Register          |        |
| 0b100001RR   | 0x84 | Register OR Value                                 | Register OR Value                   | ORV  | OR    | Register, Value   |        |
| 0b100010RR   | 0x88 | Register OR Address                               | Register OR Address                 | ORA  | OR    | Register, Address |        |
| 0b100011RR   | 0x8c | Register OR Address                               | R0 = Register OR R0                 | ORR  | OR    | Register          |        |
| 0b100100RR   | 0x90 | Register XOR Value                                | Register XOR Value                  | XORV | XOR   | Register, Value   |        |
| 0b100101RR   | 0x94 | Register XOR Address                              | Register XOR Address                | XORA | XOR   | Register, Address |        |
| 0b100110RR   | 0x98 | Register XOR Address                              | R0 = Register XOR R0                | XORR | XOR   | Register          |        |
| 0b100111RR   | 0x9c | From RR to R0                                     | R0 = RR                             | LDZ  |       | Register          |        |
| 0b101000RR   | 0xa0 | From R0 to RR                                     | RR = R0                             | STZ  |       | Register          |        |
|              |      |                                                   |                                     |      |       |                   |        |
| Stack        |      |                                                   |                                     |      |       |                   |        |
| 0b101001RR   | 0xa4 | Push Register to stack                            | Push Register                       | PSHR | PSH   | Register          |        |
| 0b101010RR   | 0xa8 | Pop register to stack                             | Pop Register                        | POPR | POP   | Register          |        |
| 0b10101100   | 0xac | Push all registers to stack                       | Push All                            | PSHA | PSH   | None              | PASS   |
| 0b10101101   | 0xad | Pop all registers from stack                      | Pop All                             | POPA | POP   | None              | PASS   |
|              |      |                                                   |                                     |      |       |                   |        |
|              |      |                                                   |                                     |      |       |                   |        |
| Conditionals |      |                                                   |                                     |      |       |                   |        |
| 0b10101110   | 0xae |                                                   | Cond Address=0                      | CEZA | CEZ   | Address           |        |
| 0b10101111   | 0xaf |                                                   | Cond Address!=0                     | CNZA | CNZ   | Address           |        |
| 0b101100RR   | 0xb0 |                                                   | Cond Register=0                     | CEZR | CEZ   | Register          | PASS   |
| 0b101101RR   | 0xb4 |                                                   | Cond Register!=0                    | CNZR | CNZ   | Register          | PASS   |
| 0b101110RR   | 0xb8 |                                                   | Cond Register=Value                 | CEV  | CE    | Register, Value   |        |
| 0b101111RR   | 0xbc |                                                   | Cond Register=Address               | CEA  | CE    | Register, Address |        |
| 0b110000RR   | 0xc0 |                                                   | Cond Register!=Value                | CNV  | CNE   | Register, Value   |        |
| 0b110001RR   | 0xc4 |                                                   | Cond Register!=Address              | CNA  | CNE   | Register, Address |        |
| 0b110010RR   | 0xc8 |                                                   | Cond Register<Value                 | CLTV | CLT   | Register, Value   |        |
| 0b110011RR   | 0xcc |                                                   | Cond Register<Address               | CLTA | CLT   | Register, Address |        |
| 0b110100RR   | 0xd0 |                                                   | Cond Register>Value                 | CGTV | CGT   | Register, Value   |        |
| 0b110101RR   | 0xd4 |                                                   | Cond Register>Address               | CGTA | CGT   | Register, Address |        |
|              |      |                                                   |                                     |      |       |                   |        |
| Control Flow |      |                                                   |                                     |      |       |                   |        |
| 0b11011000   | 0xd8 |                                                   | Jump Address                        | JMPA | JMP   | Value             |        |
| 0b11011001   | 0xd9 |                                                   | Jump AddressRegister                | JMPD | JMP   | None              | PASS   |
| 0b11011010   | 0xda |                                                   | Routine Address                     | CALA | CALL  | Value             | PASS   |
| 0b11011011   | 0xdb |                                                   | Routine AddressRegister             | CALD | CALL  | None              |        |
| 0b11011100   | 0xdc |                                                   | Return                              | RET  |       | None              | PASS   |
| 0b11011101   | 0xdd |                                                   | Jump Conditional Address            | JPCA | JMPC  | Value             | PASS   |
| 0b11011110   | 0xde |                                                   | Jump Conditional AddressRegister    | JPCD | JMPC  | None              |        |
| 0b11011111   | 0xdf |                                                   | Routine Conditional Address         | CLCA | CALLC | Value             | PASS   |
| 0b11100000   | 0xe0 |                                                   | Routine Conditional AddressRegister | CLCD | CALLC | None              |        |
| 0b11100001   | 0xe1 |                                                   | Return Conditional                  | RETC |       | None              |        |
| 0b11100010   | 0xe2 |                                                   | Break                               | BRK  |       | None              | NYI    |
| 0b11100011   | 0xe3 |                                                   | Halt                                | HLT  |       | None              | PASS   |
|              |      |                                                   |                                     |      |       |                   |        |
| Extended     |      |                                                   |                                     |      |       |                   |        |
| 0b111001RR   | 0xe4 | Send register to the debugging terminal           | Register → DBG                      | DBGR | DBG   | Register          |        |
| 0b11101000   | 0xe8 | Output value to the debugging terminal            | Value → DBG                         | DBGV | DBG   | Value             | PASS   |
| 0b11101001   | 0xe9 | Output address to the debugging terminal          | Address → DBG                       | DBGA | DBG   | Address           |        |
| 0b11101010   | 0xea | Output address to the debugging terminal as char  | Address → DBG (Char)                | DBCA | DBGC  | Address           |        |
| 0b11101011   | 0xeb | Output value to the debugging terminal as char    | Value → DBG (Char)                  | DBCV | DBGC  | Value             | PASS   |
| 0b111011RR   | 0xec | Send register to the debugging terminal as char   | Register → DBG (Char)               | DBCR | DBGC  | Register          |        |
| 0b111100RR   | 0xf0 | Load register to AddressOffset                    | Register → AddressOffset            | ADOR | ADO   | Register          | PASS   |
| 0b11110100   | 0xf4 | Load value to AddressOffset                       | Value → AddressOffset               | ADOV | ADO   | Value             | PASS   |
| 0b11110101   | 0xf5 | Load address to AddressOffset                     | Address → AddressOffset             | ADOA | ADO   | Address           | PASS   |
| 0b11110110   | 0xf6 | Increment the addressRegister                     |                                     | INCD |       | None              |        |
| 0b11110111   | 0xf7 | Decrement the addressRegister                     |                                     | DECD |       | None              |        |
| 0b11111000   | 0xf8 | Disable Interrupts                                |                                     | IDIS |       | None              |        |
| 0b11111001   | 0xf9 | Enable Interrupts                                 |                                     | IEN  |       | None              |        |
| 0b11111010   | 0xfa | Copy the AO into R0                               |                                     | ADO  |       | None              |        |
