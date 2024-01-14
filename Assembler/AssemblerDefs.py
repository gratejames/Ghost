Instructions = {
    "NOP": {
        "Binary": "0b00000000",
        "Arguments": "None"
    },
    "STV": {
        "Binary": "0b00000010",
        "Arguments": "Value Address"
    },
    "STA": {
        "Binary": "0b00000011",
        "Arguments": "Address Address"
    },
    "PSHA": {
        "Binary": "0b00000100",
        "Arguments": "None"
    },
    "POPA": {
        "Binary": "0b00000101",
        "Arguments": "None"
    },
    "CEZA": {
        "Binary": "0b00000110",
        "Arguments": "Address"
    },
    "CNZA": {
        "Binary": "0b00000111",
        "Arguments": "Address"
    },
    "DBCA": {
        "Binary": "0b00001000",
        "Arguments": "Address"
    },
    "DBGA": {
        "Binary": "0b00001001",
        "Arguments": "Address"
    },
    "DBCV": {
        "Binary": "0b00001010",
        "Arguments": "Value"
    },
    "DBGV": {
        "Binary": "0b00001011",
        "Arguments": "Value"
    },
    "STR": {
        "Binary": "0b000011RR",
        "Arguments": "Register Address"
    },
    "DBCR": {
        "Binary": "0b000100RR",
        "Arguments": "Register"
    },
    "DBGR": {
        "Binary": "0b000101RR",
        "Arguments": "Register"
    },
    "CEZR": {
        "Binary": "0b000110RR",
        "Arguments": "Register"
    },
    "CNZR": {
        "Binary": "0b000111RR",
        "Arguments": "Register"
    },
    "LDV": {
        "Binary": "0b001000RR",
        "Arguments": "Register Value"
    },
    "LDA": {
        "Binary": "0b001001RR",
        "Arguments": "Register Address"
    },
    "PSHR": {
        "Binary": "0b001010RR",
        "Arguments": "Register"
    },
    "POPR": {
        "Binary": "0b001011RR",
        "Arguments": "Register"
    },
    "ST0AR": {
        "Binary": "0b001100RR",
        "Arguments": "Register"
    },
    "ST1AR": {
        "Binary": "0b001101RR",
        "Arguments": "Register"
    },
    "ST2AR": {
        "Binary": "0b001110RR",
        "Arguments": "Register"
    },
    "ST3AR": {
        "Binary": "0b001111RR",
        "Arguments": "Register"
    },
    "CEA": {
        "Binary": "0b010000RR",
        "Arguments": "Register Address"
    },
    "CNA": {
        "Binary": "0b010001RR",
        "Arguments": "Register Address"
    },
    "CLTA": {
        "Binary": "0b010010RR",
        "Arguments": "Register Address"
    },
    "CGTA": {
        "Binary": "0b010011RR",
        "Arguments": "Register Address"
    },
    "CEV": {
        "Binary": "0b010100RR",
        "Arguments": "Register Value"
    },
    "CNV": {
        "Binary": "0b010101RR",
        "Arguments": "Register Value"
    },
    "CLTV": {
        "Binary": "0b010110RR",
        "Arguments": "Register Value"
    },
    "CGTV": {
        "Binary": "0b010111RR",
        "Arguments": "Register Value"
    },
    "JPRD": {
        "Binary": "0b011000RR",
        "Arguments": "Register"
    },
    "JPRC": {
        "Binary": "0b011001RR",
        "Arguments": "Register"
    },
    "CLRD": {
        "Binary": "0b011010RR",
        "Arguments": "Register"
    },
    "CLRC": {
        "Binary": "0b011011RR",
        "Arguments": "Register"
    },
    "JPVD": {
        "Binary": "0b01110000",
        "Arguments": "Value"
    },
    "INTD": {
        "Binary": "0b01110001",
        "Arguments": "Value"
    },
    "RETD": {
        "Binary": "0b01110010",
        "Arguments": "None"
    },
    "HLTD": {
        "Binary": "0b01110011",
        "Arguments": "None"
    },
    "JPVC": {
        "Binary": "0b01110100",
        "Arguments": "Value"
    },
    "INTC": {
        "Binary": "0b01110101",
        "Arguments": "Value"
    },
    "RETC": {
        "Binary": "0b01110110",
        "Arguments": "None"
    },
    "HLTC": {
        "Binary": "0b01110111",
        "Arguments": "None"
    },
    "CLVD": {
        "Binary": "0b01111000",
        "Arguments": "Value"
    },
    "BRKD": {
        "Binary": "0b01111011",
        "Arguments": "None"
    },
    "CLVC": {
        "Binary": "0b01111100",
        "Arguments": "Value"
    },
    "BRKC": {
        "Binary": "0b01111111",
        "Arguments": "None"
    },
    "ADDA": {
        "Binary": "0b100000RR",
        "Arguments": "Register Address"
    },
    "SUBA": {
        "Binary": "0b100001RR",
        "Arguments": "Register Address"
    },
    "SHLA": {
        "Binary": "0b100010RR",
        "Arguments": "Register Address"
    },
    "SHRA": {
        "Binary": "0b100011RR",
        "Arguments": "Register Address"
    },
    "ANDA": {
        "Binary": "0b100100RR",
        "Arguments": "Register Address"
    },
    "SBRA": {
        "Binary": "0b100101RR",
        "Arguments": "Register Address"
    },
    "ORA": {
        "Binary": "0b100110RR",
        "Arguments": "Register Address"
    },
    "XORA": {
        "Binary": "0b100111RR",
        "Arguments": "Register Address"
    },
    "ADDV": {
        "Binary": "0b101000RR",
        "Arguments": "Register Value"
    },
    "SUBV": {
        "Binary": "0b101001RR",
        "Arguments": "Register Value"
    },
    "SHLV": {
        "Binary": "0b101010RR",
        "Arguments": "Register Value"
    },
    "SHRV": {
        "Binary": "0b101011RR",
        "Arguments": "Register Value"
    },
    "ANDV": {
        "Binary": "0b101100RR",
        "Arguments": "Register Value"
    },
    "SBRV": {
        "Binary": "0b101101RR",
        "Arguments": "Register Value"
    },
    "ORV": {
        "Binary": "0b101110RR",
        "Arguments": "Register Value"
    },
    "XORV": {
        "Binary": "0b101111RR",
        "Arguments": "Register Value"
    },
    "ADDR": {
        "Binary": "0b110000RR",
        "Arguments": "Register"
    },
    "SUBR": {
        "Binary": "0b110001RR",
        "Arguments": "Register"
    },
    "SHLR": {
        "Binary": "0b110010RR",
        "Arguments": "Register"
    },
    "SHRR": {
        "Binary": "0b110011RR",
        "Arguments": "Register"
    },
    "ANDR": {
        "Binary": "0b110100RR",
        "Arguments": "Register"
    },
    "SBRR": {
        "Binary": "0b110101RR",
        "Arguments": "Register"
    },
    "ORR": {
        "Binary": "0b110110RR",
        "Arguments": "Register"
    },
    "XORR": {
        "Binary": "0b110111RR",
        "Arguments": "Register"
    },
    "INC": {
        "Binary": "0b111000RR",
        "Arguments": "Register"
    },
    "DEC": {
        "Binary": "0b111001RR",
        "Arguments": "Register"
    },
    "SHLO": {
        "Binary": "0b111010RR",
        "Arguments": "Register"
    },
    "SHRO": {
        "Binary": "0b111011RR",
        "Arguments": "Register"
    },
    "ZERO": {
        "Binary": "0b111100RR",
        "Arguments": "Register"
    },
    "NEG": {
        "Binary": "0b111101RR",
        "Arguments": "Register"
    },
    "FULL": {
        "Binary": "0b111110RR",
        "Arguments": "Register"
    },
    "NOT": {
        "Binary": "0b111111RR",
        "Arguments": "Register"
    }
}
Shorthand = {
    "ST": {
        "Value Address": "STV",
        "Address Address": "STA",
        "Register Address": "STR"
    },
    "PSH": {
        "None": "PSHA",
        "Register": "PSHR"
    },
    "POP": {
        "None": "POPA",
        "Register": "POPR"
    },
    "CEZ": {
        "Address": "CEZA",
        "Register": "CEZR"
    },
    "CNZ": {
        "Address": "CNZA",
        "Register": "CNZR"
    },
    "DBGC": {
        "Address": "DBCA",
        "Value": "DBCV",
        "Register": "DBCR"
    },
    "DBG": {
        "Address": "DBGA",
        "Value": "DBGV",
        "Register": "DBGR"
    },
    "LD": {
        "Register Value": "LDV",
        "Register Address": "LDA"
    },
    "STRR": {
        "Register": "ST3AR"
    },
    "CE": {
        "Register Address": "CEA",
        "Register Value": "CEV"
    },
    "CNE": {
        "Register Address": "CNA",
        "Register Value": "CNV"
    },
    "CLE": {
        "Register Address": "CLTA",
        "Register Value": "CLTV"
    },
    "CGE": {
        "Register Address": "CGTA",
        "Register Value": "CGTV"
    },
    "JMP": {
        "Register": "JPRD",
        "Value": "JPVD"
    },
    "JMPC": {
        "Register": "JPRC",
        "Value": "JPVC"
    },
    "CALL": {
        "Register": "CLRD",
        "Value": "CLVD"
    },
    "CALLC": {
        "Register": "CLRC",
        "Value": "CLVC"
    },
    "INT": {
        "Value": "INTD"
    },
    "RET": {
        "None": "RETD"
    },
    "HLT": {
        "None": "HLTD"
    },
    "BRK": {
        "None": "BRKD"
    },
    "ADD": {
        "Register Address": "ADDA",
        "Register Value": "ADDV",
        "Register": "ADDR"
    },
    "SUB": {
        "Register Address": "SUBA",
        "Register Value": "SUBV",
        "Register": "SUBR"
    },
    "SHL": {
        "Register Address": "SHLA",
        "Register Value": "SHLV",
        "Register": "SHLR"
    },
    "SHR": {
        "Register Address": "SHRA",
        "Register Value": "SHRV",
        "Register": "SHRR"
    },
    "AND": {
        "Register Address": "ANDA",
        "Register Value": "ANDV",
        "Register": "ANDR"
    },
    "SBR": {
        "Register Address": "SBRA",
        "Register Value": "SBRV",
        "Register": "SBRR"
    },
    "OR": {
        "Register Address": "ORA",
        "Register Value": "ORV",
        "Register": "ORR"
    },
    "XOR": {
        "Register Address": "XORA",
        "Register Value": "XORV",
        "Register": "XORR"
    },
    "INC": {
        "Register": "INC"
    }
}
