0b0000 0000 NOP

0b0000 0001 ??

0b0000 001- Store Immediate to Address
0   Value or Address

0b0000 010- Stack All
0   Push or Pop

0b0000 011- Compare Immediate Zero
0   Equal or Not

0b0000 10-- Debug Immediate
0   Address or Value
0   Char or Hex

0b0000 11-- Store Register to Address
00  Register

0b0001 0--- Debug Register
0   Char or Hex
00  Register

0b0001 1--- Compare Register Zero
0   Equal or Not
00  Register

0b0010 0--- Load Immediate to $RR
0   Address or Value
00  Register

0b0010 1--- Stack Single
0   Push or Pop
00  Register

0b0011 ---- RR to $RR
00 From Register
00 Register with Address

0b010- ---- Compare RR to Immediate
0   Address or Value
0   Equality or Comparison
0   =/! if equality, <\/> if comparison
00  Register

0b011- ---- Control Flow
0   Register or Other
0   Jump or Call
0   Definite or Conditional
00  Register or 00 = next byte, 01 = INT, 10 = stack (RET), 11 = Stop (HLT if Jump, Break if Call)

0b1--- ---- Math
0   Immediate or Other
0   Address/Value or R0/Monadic (hardcoded value given in hex below)
000 x01: (+, -, SHL, SHR) 0x00: (AND, -R) xff: (OR, XOR)
00  Register


Dyadic to Monadic Math:
| Op    | Arg2 | Outcome |
| ----- | ---- | ------- |
| -/+   | 0x01 | inc/dec |
| SHL/R | 0x01 | SHL1/R1 |
| XOR   | 0xff | NOT     |
| OR    | 0xff | ff      |
| -R    | 0x00 | NEG     |
| AND   | 0x00 | 0       |