void OUT(char* stringy) {
    stringy;
    asm {
DD R0
%loop:
LDD R1
CEZ R1
JMPC %done
DBGC R1
INCD
JMP %loop
%done:
    }
}

void OUTLN(char* stringy) {
    OUT(stringy);
    asm { DBGC 0xa }
}