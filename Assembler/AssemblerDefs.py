Instructions = {
    "NOP": {
        "Binary": "0b00000000",
        "Arguments": "None"
    },
    "MVAA": {
        "Binary": "0b00000001",
        "Arguments": "Address Address"
    },
    "DDV": {
        "Binary": "0b00000010",
        "Arguments": "Value"
    },
    "DDA": {
        "Binary": "0b00000011",
        "Arguments": "Address"
    },
    "DDR": {
        "Binary": "0b000001RR",
        "Arguments": "Register"
    },
    "LDV": {
        "Binary": "0b000010RR",
        "Arguments": "Register Value"
    },
    "LDA": {
        "Binary": "0b000011RR",
        "Arguments": "Register Address"
    },
    "LDD": {
        "Binary": "0b000100RR",
        "Arguments": "Register"
    },
    "STR": {
        "Binary": "0b000101RR",
        "Arguments": "Register Address"
    },
    "STAR": {
        "Binary": "0b000110RR",
        "Arguments": "Register Value"
    },
    "STV": {
        "Binary": "0b00011100",
        "Arguments": "Value Address"
    },
    "STDV": {
        "Binary": "0b00011101",
        "Arguments": "Value"
    },
    "MVDD": {
        "Binary": "0b00011110",
        "Arguments": "Address"
    },
    "INT": {
        "Binary": "0b00011111",
        "Arguments": "Value"
    },
    "STDR": {
        "Binary": "0b001000RR",
        "Arguments": "Register"
    },
    "SHLV": {
        "Binary": "0b001001RR",
        "Arguments": "Register Value"
    },
    "SHLA": {
        "Binary": "0b001010RR",
        "Arguments": "Register Address"
    },
    "SHLR": {
        "Binary": "0b001011RR",
        "Arguments": "Register"
    },
    "SHRV": {
        "Binary": "0b001100RR",
        "Arguments": "Register Value"
    },
    "SHRA": {
        "Binary": "0b001101RR",
        "Arguments": "Register Address"
    },
    "SHRR": {
        "Binary": "0b001110RR",
        "Arguments": "Register"
    },
    "ADDV": {
        "Binary": "0b001111RR",
        "Arguments": "Register Value"
    },
    "ADDA": {
        "Binary": "0b010000RR",
        "Arguments": "Register Address"
    },
    "ADDR": {
        "Binary": "0b010001RR",
        "Arguments": "Register"
    },
    "SUBV": {
        "Binary": "0b010010RR",
        "Arguments": "Register Value"
    },
    "SUBA": {
        "Binary": "0b010011RR",
        "Arguments": "Register Address"
    },
    "SUBR": {
        "Binary": "0b010100RR",
        "Arguments": "Register"
    },
    "SBRV": {
        "Binary": "0b010101RR",
        "Arguments": "Register Value"
    },
    "SBRA": {
        "Binary": "0b010110RR",
        "Arguments": "Register Address"
    },
    "SBRR": {
        "Binary": "0b010111RR",
        "Arguments": "Register"
    },
    "NOT": {
        "Binary": "0b011000RR",
        "Arguments": "Register"
    },
    "PSHA": {
        "Binary": "0b01100100",
        "Arguments": "None"
    },
    "POPA": {
        "Binary": "0b01100110",
        "Arguments": "None"
    },
    "INC": {
        "Binary": "0b011010RR",
        "Arguments": "Register"
    },
    "DEC": {
        "Binary": "0b011011RR",
        "Arguments": "Register"
    },
    "SHLO": {
        "Binary": "0b011100RR",
        "Arguments": "Register"
    },
    "SHRO": {
        "Binary": "0b011101RR",
        "Arguments": "Register"
    },
    "ANDV": {
        "Binary": "0b011110RR",
        "Arguments": "Register Value"
    },
    "ANDA": {
        "Binary": "0b011111RR",
        "Arguments": "Register Address"
    },
    "ANDR": {
        "Binary": "0b100000RR",
        "Arguments": "Register"
    },
    "ORV": {
        "Binary": "0b100001RR",
        "Arguments": "Register Value"
    },
    "ORA": {
        "Binary": "0b100010RR",
        "Arguments": "Register Address"
    },
    "ORR": {
        "Binary": "0b100011RR",
        "Arguments": "Register"
    },
    "XORV": {
        "Binary": "0b100100RR",
        "Arguments": "Register Value"
    },
    "XORA": {
        "Binary": "0b100101RR",
        "Arguments": "Register Address"
    },
    "XORR": {
        "Binary": "0b100110RR",
        "Arguments": "Register"
    },
    "LDZ": {
        "Binary": "0b100111RR",
        "Arguments": "Register"
    },
    "STZ": {
        "Binary": "0b101000RR",
        "Arguments": "Register"
    },
    "PSHR": {
        "Binary": "0b101001RR",
        "Arguments": "Register"
    },
    "POPR": {
        "Binary": "0b101010RR",
        "Arguments": "Register"
    },
    "LDSP": {
        "Binary": "0b10101100",
        "Arguments": "None"
    },
    "STSP": {
        "Binary": "0b10101101",
        "Arguments": "None"
    },
    "CEZA": {
        "Binary": "0b10101110",
        "Arguments": "Address"
    },
    "CNZA": {
        "Binary": "0b10101111",
        "Arguments": "Address"
    },
    "CEZR": {
        "Binary": "0b101100RR",
        "Arguments": "Register"
    },
    "CNZR": {
        "Binary": "0b101101RR",
        "Arguments": "Register"
    },
    "CEV": {
        "Binary": "0b101110RR",
        "Arguments": "Register Value"
    },
    "CEA": {
        "Binary": "0b101111RR",
        "Arguments": "Register Address"
    },
    "CNV": {
        "Binary": "0b110000RR",
        "Arguments": "Register Value"
    },
    "CNA": {
        "Binary": "0b110001RR",
        "Arguments": "Register Address"
    },
    "CLTV": {
        "Binary": "0b110010RR",
        "Arguments": "Register Value"
    },
    "CLTA": {
        "Binary": "0b110011RR",
        "Arguments": "Register Address"
    },
    "CGTV": {
        "Binary": "0b110100RR",
        "Arguments": "Register Value"
    },
    "CGTA": {
        "Binary": "0b110101RR",
        "Arguments": "Register Address"
    },
    "JMPA": {
        "Binary": "0b11011000",
        "Arguments": "Value"
    },
    "JMPD": {
        "Binary": "0b11011001",
        "Arguments": "None"
    },
    "CALA": {
        "Binary": "0b11011010",
        "Arguments": "Value"
    },
    "CALD": {
        "Binary": "0b11011011",
        "Arguments": "None"
    },
    "RET": {
        "Binary": "0b11011100",
        "Arguments": "None"
    },
    "JPCA": {
        "Binary": "0b11011101",
        "Arguments": "Value"
    },
    "JPCD": {
        "Binary": "0b11011110",
        "Arguments": "None"
    },
    "CLCA": {
        "Binary": "0b11011111",
        "Arguments": "Value"
    },
    "CLCD": {
        "Binary": "0b11100000",
        "Arguments": "None"
    },
    "RETC": {
        "Binary": "0b11100001",
        "Arguments": "None"
    },
    "BRK": {
        "Binary": "0b11100010",
        "Arguments": "None"
    },
    "HLT": {
        "Binary": "0b11100011",
        "Arguments": "None"
    },
    "DBGR": {
        "Binary": "0b111001RR",
        "Arguments": "Register"
    },
    "DBGV": {
        "Binary": "0b11101000",
        "Arguments": "Value"
    },
    "DBGA": {
        "Binary": "0b11101001",
        "Arguments": "Address"
    },
    "DBCA": {
        "Binary": "0b11101010",
        "Arguments": "Address"
    },
    "DBCV": {
        "Binary": "0b11101011",
        "Arguments": "Value"
    },
    "DBCR": {
        "Binary": "0b111011RR",
        "Arguments": "Register"
    },
    "ADOR": {
        "Binary": "0b111100RR",
        "Arguments": "Register"
    },
    "ADOV": {
        "Binary": "0b11110100",
        "Arguments": "Value"
    },
    "ADOA": {
        "Binary": "0b11110101",
        "Arguments": "Address"
    },
    "INCD": {
        "Binary": "0b11110110",
        "Arguments": "None"
    },
    "DECD": {
        "Binary": "0b11110111",
        "Arguments": "None"
    },
    "IDIS": {
        "Binary": "0b11111000",
        "Arguments": "None"
    },
    "IEN": {
        "Binary": "0b11111001",
        "Arguments": "None"
    },
    "AOR": {
        "Binary": "0b11111010",
        "Arguments": "None"
    },
    "CPSH": {
        "Binary": "0b11111011",
        "Arguments": "None"
    },
    "CPOP": {
        "Binary": "0b11111100",
        "Arguments": "None"
    }
}
Shorthand = {
    "MV": {
        "Address Address": "MVAA",
        "Address": "MVDD"
    },
    "DD": {
        "Value": "DDV",
        "Address": "DDA",
        "Register": "DDR"
    },
    "LD": {
        "Register Value": "LDV",
        "Register Address": "LDA",
        "Register": "LDD"
    },
    "ST": {
        "Register Address": "STR",
        "Register Value": "STAR",
        "Value Address": "STV"
    },
    "STD": {
        "Value": "STDV",
        "Register": "STDR"
    },
    "SHL": {
        "Register Value": "SHLV",
        "Register Address": "SHLA",
        "Register": "SHLR"
    },
    "SHR": {
        "Register Value": "SHRV",
        "Register Address": "SHRA",
        "Register": "SHRR"
    },
    "ADD": {
        "Register Value": "ADDV",
        "Register Address": "ADDA",
        "Register": "ADDR"
    },
    "SUB": {
        "Register Value": "SUBV",
        "Register Address": "SUBA",
        "Register": "SUBR"
    },
    "SBR": {
        "Register Value": "SBRV",
        "Register Address": "SBRA",
        "Register": "SBRR"
    },
    "PSH": {
        "None": "PSHA",
        "Register": "PSHR"
    },
    "POP": {
        "None": "POPA",
        "Register": "POPR"
    },
    "AND": {
        "Register Value": "ANDV",
        "Register Address": "ANDA",
        "Register": "ANDR"
    },
    "OR": {
        "Register Value": "ORV",
        "Register Address": "ORA",
        "Register": "ORR"
    },
    "XOR": {
        "Register Value": "XORV",
        "Register Address": "XORA",
        "Register": "XORR"
    },
    "CEZ": {
        "Address": "CEZA",
        "Register": "CEZR"
    },
    "CNZ": {
        "Address": "CNZA",
        "Register": "CNZR"
    },
    "CE": {
        "Register Value": "CEV",
        "Register Address": "CEA"
    },
    "CNE": {
        "Register Value": "CNV",
        "Register Address": "CNA"
    },
    "CLT": {
        "Register Value": "CLTV",
        "Register Address": "CLTA"
    },
    "CGT": {
        "Register Value": "CGTV",
        "Register Address": "CGTA"
    },
    "JMP": {
        "Value": "JMPA",
        "None": "JMPD"
    },
    "CALL": {
        "Value": "CALA",
        "None": "CALD"
    },
    "JMPC": {
        "Value": "JPCA",
        "None": "JPCD"
    },
    "CALLC": {
        "Value": "CLCA",
        "None": "CLCD"
    },
    "DBG": {
        "Register": "DBGR",
        "Value": "DBGV",
        "Address": "DBGA"
    },
    "DBGC": {
        "Address": "DBCA",
        "Value": "DBCV",
        "Register": "DBCR"
    },
    "ADO": {
        "Register": "ADOR",
        "Value": "ADOV",
        "Address": "ADOA"
    }
}
