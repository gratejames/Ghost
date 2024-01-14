| Instruction | Hex  | Description                       | Action                  | Mnem  | Short | Arguments         |
| ----------- | ---- | --------------------------------- | ----------------------- | ----- | ----- | ----------------- |
| Basic       |      |                                   |                         |       |       |                   |
| 0b00000000  | 0x00 | No Operation                      | No Operation            | NOP   |       | None              |
| 0b00000001  | 0x01 |                                   | Unused                  |       |       |                   |
| 0b00000010  | 0x02 | Store.Value                       |                         | STV   | ST    | Value, Address             |
| 0b00000011  | 0x03 | Store.Address                     |                         | STA   | ST    | Address, Address           |
| 0b00000100  | 0x04 | Stack.Push.All                    |                         | PSHA  | PSH   | None              |
| 0b00000101  | 0x05 | Stack.Pop.All                     |                         | POPA  | POP   | None              |
| 0b00000110  | 0x06 | Compare.equal0.Address            |                         | CEZA  | CEZ   | Address             |
| 0b00000111  | 0x07 | Compare.not0.Address              |                         | CNZA  | CNZ   | Address             |
| 0b00001000  | 0x08 | Debug.Address.Char                |                         | DBCA | DBGC  | Address           |
| 0b00001001  | 0x09 | Debug.Address.Hex                 |                         | DBGA  | DBG   | Address           |
| 0b00001010  | 0x0a | Debug.Value.Char                  |                         | DBCV | DBGC  | Value             |
| 0b00001011  | 0x0b | Debug.Value.Hex                   |                         | DBGV  | DBG   | Value             |
| 0b000011RR  | 0x0c | Store.RR                          |                         | STR   | ST    | Register, Address          |
|             |      |                                   |                         |       |       |                   |
| Debug RR    |      |                                   |                         |       |       |                   |
| 0b000100RR  | 0x10 | Debug.char.RR                     |                         | DBCR | DBGC  | Register          |
| 0b000101RR  | 0x14 | Debug.hex.RR                      |                         | DBGR  | DBG   | Register          |
|             |      |                                   |                         |       |       |                   |
| Compare RR0 |      |                                   |                         |       |       |                   |
| 0b000110RR  | 0x18 | Compare.equal0.RR                 |                         | CEZR  | CEZ   | Register          |
| 0b000111RR  | 0x1c | Compare.not0.RR                   |                         | CNZR  | CNZ   | Register          |
|             |      |                                   |                         |       |       |                   |
| Load        |      |                                   |                         |       |       |                   |
| 0b001000RR  | 0x20 | Load.Value.RR                     |                         | LDV   | LD    | Register, Value   |
| 0b001001RR  | 0x24 | Load.Address.RR                   |                         | LDA   | LD    | Register, Address |
|             |      |                                   |                         |       |       |                   |
| Stack RR    |      |                                   |                         |       |       |                   |
| 0b001010RR  | 0x28 | Stack.Push.RR                     |                         | PSHR  | PSH   | Register          |
| 0b001011RR  | 0x2c | Stack.Pop.RR                      |                         | POPR  | POP   | Register          |
|             |      |                                   |                         |       |       |                   |
| RR to $RR   |      |                                   |                         |       |       |                   |
| 0b001100RR  | 0x30 | Move.R0.RR                        |                         | ST0AR | STRR  | Register          |
| 0b001101RR  | 0x34 | Move.R1.RR                        |                         | ST1AR | STRR  | Register          |
| 0b001110RR  | 0x38 | Move.R2.RR                        |                         | ST2AR | STRR  | Register          |
| 0b001111RR  | 0x3c | Move.R3.RR                        |                         | ST3AR | STRR  | Register          |
|             |      |                                   |                         |       |       |                   |
| Compare RR  |      |                                   |                         |       |       |                   |
| 0b010000RR  | 0x40 | Compare.Address.Equal.RR          |                         | CEA   | CE    | Register, Address |
| 0b010001RR  | 0x44 | Compare.Address.NotEqual.RR       |                         | CNA   | CNE   | Register, Address |
| 0b010010RR  | 0x48 | Compare.Address.Less.RR           |                         | CLTA   | CLE   | Register, Address |
| 0b010011RR  | 0x4c | Compare.Address.Great.RR          |                         | CGTA   | CGE   | Register, Address |
| 0b010100RR  | 0x50 | Compare.Value.Equal.RR            |                         | CEV   | CE    | Register, Value   |
| 0b010101RR  | 0x54 | Compare.Value.NotEqual.RR         |                         | CNV   | CNE   | Register, Value   |
| 0b010110RR  | 0x58 | Compare.Value.Less.RR             |                         | CLTV   | CLE   | Register, Value   |
| 0b010111RR  | 0x5c | Compare.Value.Great.RR            |                         | CGTV   | CGE   | Register, Value   |
|             |      |                                   |                         |       |       |                   |
| Control     |      |                                   |                         |       |       |                   |
| 0b011000RR  | 0x60 | Ctrl.Register.Jump.Definite.RR    |                         | JPRD  | JMP   | Register          |
| 0b011001RR  | 0x64 | Ctrl.Register.Jump.Conditional.RR |                         | JPRC | JMPC  | Register          |
| 0b011010RR  | 0x68 | Ctrl.Register.Call.Definite.RR    |                         | CLRD  | CALL  | Register          |
| 0b011011RR  | 0x6c | Ctrl.Register.Call.Conditional.RR |                         | CLRC | CALLC | Register          |
| 0b01110000  | 0x70 | Ctrl.Other.Jump.Definite.Value    |                         | JPVD  | JMP   | Value             |
| 0b01110001  | 0x71 | Ctrl.Other.Jump.Definite.Int      |                         | INTD   | INT      | Value             |
| 0b01110010  | 0x72 | Ctrl.Other.Jump.Definite.Stack    |                         | RETD   | RET      | None              |
| 0b01110011  | 0x73 | Ctrl.Other.Jump.Definite.Stop     |                         | HLTD   | HLT      | None              |
| 0b01110100  | 0x74 | Ctrl.Other.Jump.Conditional.Value |                         | JPVC | JMPC  | Value             |
| 0b01110101  | 0x75 | Ctrl.Other.Jump.Conditional.Int   |                         | INTC  |       | Value             |
| 0b01110110  | 0x76 | Ctrl.Other.Jump.Conditional.Stack |                         | RETC  |       | None              |
| 0b01110111  | 0x77 | Ctrl.Other.Jump.Conditional.Stop  |                         | HLTC  |       | None              |
| 0b01111000  | 0x78 | Ctrl.Other.Call.Definite.Value    |                         | CLVD  | CALL  | Value             |
| 0b01111001  | 0x79 | Ctrl.Other.Call.Definite.Int      | Unused                  |       |       |                   |
| 0b01111010  | 0x7a | Ctrl.Other.Call.Definite.Stack    | Unused                  |       |       |                   |
| 0b01111011  | 0x7b | Ctrl.Other.Call.Definite.Stop     |                         | BRKD   | BRK      | None              |
| 0b01111100  | 0x7c | Ctrl.Other.Call.Conditional.Value |                         | CLVC | CALLC | Value             |
| 0b01111101  | 0x7d | Ctrl.Other.Call.Conditional.Int   | Unused                  |       |       |                   |
| 0b01111110  | 0x7e | Ctrl.Other.Call.Conditional.Stack | Unused                  |       |       |                   |
| 0b01111111  | 0x7f | Ctrl.Other.Call.Conditional.Stop  |                         | BRKC  |       | None              |
|             |      |                                   |                         |       |       |                   |
|             |      |                                   |                         |       |       |                   |
| Math        |      |                                   |                         |       |       |                   |
| 0b100000RR  | 0x80 | Math.Register.Address.Add.RR      | Register + Address      | ADDA  | ADD   | Register, Address |
| 0b100001RR  | 0x84 | Math.Register.Address.Sub.RR      | Register - Address      | SUBA  | SUB   | Register, Address |
| 0b100010RR  | 0x88 | Math.Register.Address.SHL.RR      | Register << Address     | SHLA  | SHL   | Register, Address |
| 0b100011RR  | 0x8c | Math.Register.Address.SHR.RR      | Register >> Address     | SHRA  | SHR   | Register, Address |
| 0b100100RR  | 0x90 | Math.Register.Address.AND.RR      | Register AND Address    | ANDA  | AND   | Register, Address |
| 0b100101RR  | 0x94 | Math.Register.Address.SBR.RR      | Address - Register      | SBRA  | SBR   | Register, Address |
| 0b100110RR  | 0x98 | Math.Register.Address.OR.RR       | Register or Address     | ORA   | OR    | Register, Address |
| 0b100111RR  | 0x9c | Math.Register.Address.XOR.RR      | Register xor Address    | XORA  | XOR   | Register, Address |
| 0b101000RR  | 0xa0 | Math.Register.Value.Add.RR        | Register + Value        | ADDV  | ADD   | Register, Value   |
| 0b101001RR  | 0xa4 | Math.Register.Value.Sub.RR        | Register - Value        | SUBV  | SUB   | Register, Value   |
| 0b101010RR  | 0xa8 | Math.Register.Value.SHL.RR        | Register << Value       | SHLV  | SHL   | Register, Value   |
| 0b101011RR  | 0xac | Math.Register.Value.SHR.RR        | Register >> Value       | SHRV  | SHR   | Register, Value   |
| 0b101100RR  | 0xb0 | Math.Register.Value.AND.RR        | Register AND Value      | ANDV  | AND   | Register, Value   |
| 0b101101RR  | 0xb4 | Math.Register.Value.SBR.RR        | Address - Value         | SBRV  | SBR   | Register, Value   |
| 0b101110RR  | 0xb8 | Math.Register.Value.OR.RR         | Register or Value       | ORV   | OR    | Register, Value   |
| 0b101111RR  | 0xbc | Math.Register.Value.XOR.RR        | Register xor Value      | XORV  | XOR   | Register, Value   |
| 0b110000RR  | 0xc0 | Math.Other.R0.Add.RR              | Register + R0           | ADDR  | ADD   | Register          |
| 0b110001RR  | 0xc4 | Math.Other.R0.Sub.RR              | Register - R0           | SUBR  | SUB   | Register          |
| 0b110010RR  | 0xc8 | Math.Other.R0.SHL.RR              | Register << R0          | SHLR  | SHL   | Register          |
| 0b110011RR  | 0xcc | Math.Other.R0.SHR.RR              | Register >> R0          | SHRR  | SHR   | Register          |
| 0b110100RR  | 0xd0 | Math.Other.R0.AND.RR              | Register AND R0         | ANDR  | AND   | Register          |
| 0b110101RR  | 0xd4 | Math.Other.R0.SBR.RR              | Address - R0            | SBRR  | SBR   | Register          |
| 0b110110RR  | 0xd8 | Math.Other.R0.OR.RR               | Register or R0          | ORR   | OR    | Register          |
| 0b110111RR  | 0xdc | Math.Other.R0.XOR.RR              | Register xor R0         | XORR  | XOR   | Register          |
| 0b111000RR  | 0xe0 | Math.Other.Mono.Add.RR            | Register + 1            | INC   | INC   | Register          |
| 0b111001RR  | 0xe4 | Math.Other.Mono.Sub.RR            | Register - 1            | DEC   |       | Register          |
| 0b111010RR  | 0xe8 | Math.Other.Mono.SHL.RR            | Register << 1           | SHLO  |       | Register          |
| 0b111011RR  | 0xec | Math.Other.Mono.SHR.RR            | Register >> 1           | SHRO  |       | Register          |
| 0b111100RR  | 0xf0 | Math.Other.Mono.AND.RR            | Register AND 0 (0x00)   | ZERO  |       | Register          |
| 0b111101RR  | 0xf4 | Math.Other.Mono.SBR.RR            | 0 - Value (Twos)        | NEG   |       | Register          |
| 0b111110RR  | 0xf8 | Math.Other.Mono.OR.RR             | Register or 0xff (0xff) | FULL  |       | Register          |
| 0b111111RR  | 0xfc | Math.Other.Mono.XOR.RR            | Register xor 0xff       | NOT   |       | Register          |
