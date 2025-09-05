from pathlib import Path

keywords = [
    "if",
    "else",
    "return",
    "do",
    "while",
    "for",
    "break",
    "continue",
    "true",
    "false",
    "asm",
]
types = ["void", "int", "char"]
symbols = [
    "#",
]
operators = [
    "==",
    "<=",
    ">=",
    "!=",
    ">",
    "<",
    "+",
    "^",
    "|",
    "&",
    "-",
    ",",
    "/",
    "&&",
    "||",
    "-",
    "~",
    "!",
    "*",
    ">>",
    "<<",
    "++",
    "--",
    ":",
    "?",
    "%",
]
assignment = [
    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "<<=",
    ">>=",
    "&=",
    "^=",
    "|=",
]


class Line:
    def __init__(self, contents: str, line: int, file: Path):
        self.contents = contents
        self.line = line
        self.file = file

    def __repr__(self):
        return f"{self.line}.{self.file.name}: {self.contents}"


class PreToken:
    def __init__(
        self, contents: str = "", line: int = 0, pos: int = 0, file: Path = Path()
    ):
        self.contents = contents
        self.line = line
        self.file = file
        self.pos = pos

    def __repr__(self):
        return f"('{self.contents}':{self.line}:{self.file})"

    contents: str = ""
    line: int = 0
    file: Path


def prettyPath(path: Path) -> Path:
    local = Path(".").absolute()
    path = path.absolute()
    if path.is_relative_to(local):
        return path.relative_to(local)
    else:
        return path.absolute()


class Token:
    def __init__(
        self,
        type: str,
        # contents: str | int,
        contents: str,
        tokenNumber: int,
        line: int,
        pos: int,
        file: Path,
        value: int | None = None,
    ):
        self.type = type
        self.contents = contents
        self.tokenNumber = tokenNumber
        self.line = line
        self.pos = pos
        self.file = file
        self.value = value

    def __repr__(self):
        return f"({self.type} '{self.contents}', {self.line}:{self.tokenNumber}:{self.file})"

    def blame(self):
        print("\n".join(self.blame_string()))

    def blame_string(self):
        token = self
        # print("Error:", token)
        with open(token.file, "r") as f:
            fileContents = f.read()
        tok_length = len(token.contents)
        return [
            f"in file: {prettyPath(token.file)}",
            fileContents.split("\n")[token.line - 1],
            " " * (token.pos - tok_length + 1) + "^" + "~" * (tok_length - 1),
        ]

    type: str = ""
    contents: str = ""
    tokenNumber: int = 0
    line: int = 0
    file: Path
    value: int | None


def split(fileLines: list[Line]) -> list[PreToken]:
    contents: list[PreToken] = []
    block_comment = False
    for line in fileLines:
        for charI, char in enumerate(line.contents):
            if block_comment:
                if char == "/" and prev_char == "*":
                    block_comment = False
                    continue
                else:
                    prev_char = char
                    continue
            if char == "*" and len(contents) > 0 and contents[-1].contents == "/":
                contents = contents[:-1]
                block_comment = True
                prev_char = ""
                continue
            if char == "/" and len(contents) > 0 and contents[-1].contents == "/":
                contents = contents[:-1]
                break
            if char == " " and len(contents) == 0:
                continue
            if not (char == " " and contents[-1].contents == " ") and not char == "\n":
                contents.append(PreToken(char, line.line + 1, charI, line.file))
        contents.append(PreToken(" ", line.line + 1, contents[-1].pos, line.file))
    # print(contents)

    # print("PRE TOKENS", contents)

    tokens: list[PreToken] = [PreToken("", 1)]
    stringMode: bool = False
    quoteMode: bool = False

    for i, charPair in enumerate(contents):
        char = charPair.contents
        if stringMode:
            if char == '"':
                stringMode = False
                tokens[-1].contents += '"'
                tokens[-1].line = charPair.line
                tokens[-1].pos = charPair.pos
                tokens[-1].file = charPair.file
                tokens.append(PreToken("", 0))
            else:
                tokens[-1].contents += char
        elif quoteMode:
            if char == "'":
                quoteMode = False
                tokens[-1].contents += "'"
                tokens[-1].line = charPair.line
                tokens[-1].pos = charPair.pos
                tokens[-1].file = charPair.file
                tokens.append(PreToken("", 0))
            else:
                tokens[-1].contents += char
        elif char.strip() == "":
            if tokens[-1].contents != "":
                tokens.append(PreToken("", 0))
        elif char == '"':
            if tokens[-1].contents == "":
                tokens.pop(-1)
            tokens.append(PreToken('"', charPair.line, charPair.pos, charPair.file))
            stringMode = True
        elif char == "'":
            if tokens[-1].contents == "":
                tokens.pop(-1)
            tokens.append(PreToken("'", charPair.line, charPair.pos, charPair.file))
            quoteMode = True
        elif char in "()`~!@#$%^&*()-+=[]\\{}|;:,./?><":
            if (
                char == "="
                and len(tokens) > 1
                and tokens[-1].contents
                in [
                    "=",
                    "<",
                    ">",
                    "!",
                    "+",
                    "-",
                    "&",
                    "^",
                    "|",
                    "<<",
                    ">>",
                    "*",
                    "/",
                    "%",
                ]
            ):
                tokens[-1].contents += char
                continue
            elif char == "+" and len(tokens) > 1 and tokens[-1].contents == "+":
                tokens[-1].contents += char
                continue
            elif char == "-" and len(tokens) > 1 and tokens[-1].contents == "-":
                tokens[-1].contents += char
                continue
            elif char == ">" and len(tokens) > 1 and tokens[-1].contents == ">":
                tokens[-1].contents += char
                continue
            elif char == "<" and len(tokens) > 1 and tokens[-1].contents == "<":
                tokens[-1].contents += char
                continue
            elif char == "&" and len(tokens) > 1 and tokens[-1].contents == "&":
                tokens[-1].contents += char
                continue
            elif char == "|" and len(tokens) > 1 and tokens[-1].contents == "|":
                tokens[-1].contents += char
                continue

            if tokens[-1].contents == "":
                tokens[-1].contents += char
                tokens[-1].line = charPair.line
                tokens[-1].pos = charPair.pos
                tokens[-1].file = charPair.file
            else:
                tokens.append(
                    PreToken(char, charPair.line, charPair.pos, charPair.file)
                )
        else:
            if (
                tokens[-1].contents == ""
                or tokens[-1].contents.replace("_", "").isalnum()
            ):
                tokens[-1].contents += char
                tokens[-1].line = charPair.line
                tokens[-1].pos = charPair.pos
                tokens[-1].file = charPair.file
            else:
                tokens.append(
                    PreToken(char, charPair.line, charPair.pos, charPair.file)
                )

    if tokens[-1].contents == "":
        tokens = tokens[:-1]
    return tokens


def context(c: list[PreToken]) -> list[Token]:
    tokens = []
    for tokenI, item in enumerate(c):
        # item, line_number = item.contents, item.line
        if item.contents in types:
            tokens.append(
                Token("type", item.contents, tokenI, item.line, item.pos, item.file)
            )
        elif item.contents in keywords:
            tokens.append(
                Token("keyword", item.contents, tokenI, item.line, item.pos, item.file)
            )
        elif item.contents in operators:
            tokens.append(
                Token("operator", item.contents, tokenI, item.line, item.pos, item.file)
            )
        elif item.contents in symbols:
            tokens.append(
                Token("symbol", item.contents, tokenI, item.line, item.pos, item.file)
            )
        elif item.contents.isdigit():
            tokens.append(
                Token(
                    "literal integer",
                    item.contents,
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                    int(item.contents),
                )
            )
        elif (
            len(item.contents) > 1
            and item.contents[0] == '"'
            and item.contents[-1] == '"'
        ):
            tokens.append(
                Token(
                    "literal string",
                    item.contents[1:-1],
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                )
            )
        elif (
            len(item.contents) == 3
            and item.contents[0] == "'"
            and item.contents[2] == "'"
        ):
            tokens.append(
                Token(
                    "literal char",
                    item.contents[1],
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                )
            )
        elif (
            len(item.contents) > 2
            and item.contents[0] == "0"
            and item.contents[1] in "bx"
        ):
            tokens.append(
                Token(
                    "literal integer",
                    item.contents,
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                    int(item.contents, 0),
                )
            )
        elif item.contents == "(":
            tokens.append(
                Token(
                    "open paren", item.contents, tokenI, item.line, item.pos, item.file
                )
            )
        elif item.contents == ")":
            tokens.append(
                Token(
                    "close paren", item.contents, tokenI, item.line, item.pos, item.file
                )
            )
        elif item.contents == "[":
            tokens.append(
                Token(
                    "open bracket",
                    item.contents,
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                )
            )
        elif item.contents == "]":
            tokens.append(
                Token(
                    "close bracket",
                    item.contents,
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                )
            )
        elif item.contents == "{":
            tokens.append(
                Token(
                    "open brace", item.contents, tokenI, item.line, item.pos, item.file
                )
            )
        elif item.contents == "}":
            tokens.append(
                Token(
                    "close brace", item.contents, tokenI, item.line, item.pos, item.file
                )
            )
        elif item.contents == "'":
            tokens.append(
                Token(
                    "single quote",
                    item.contents,
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                )
            )
        elif item == '"':
            tokens.append(
                Token(
                    "double quote",
                    item.contents,
                    tokenI,
                    item.line,
                    item.pos,
                    item.file,
                )
            )
        elif item.contents == ",":
            tokens.append(
                Token("comma", item.contents, tokenI, item.line, item.pos, item.file)
            )
        elif item.contents == ";":
            tokens.append(
                Token(
                    "semicolon", item.contents, tokenI, item.line, item.pos, item.file
                )
            )
        elif item.contents in assignment:
            tokens.append(
                Token(
                    "assignment", item.contents, tokenI, item.line, item.pos, item.file
                )
            )
        # elif item.contents == "asm":
        #     tokens.append(
        #         token("asm",)
        #     )
        else:
            tokens.append(
                Token(
                    "identifier", item.contents, tokenI, item.line, item.pos, item.file
                )
            )
    return tokens


def includes(fileContents: str, rootFilePath: Path) -> list[Line]:
    lines: list[Line] = []
    for i, contents in enumerate(fileContents.split("\n")):
        if contents.startswith("#include "):
            fileName = contents.replace("#include ", "", 1).strip()
            if fileName[0] == '"' and fileName[-1] == '"':
                incPath = rootFilePath.parent.absolute() / fileName[1:-1]
                if incPath.suffix not in [".g"]:
                    print("Delaying inclusion for assembler:", incPath.name)
                    lines.append(Line(contents, i, rootFilePath))
                    continue
                with open(incPath, "r") as f:
                    incFileContents = f.read()
                lines = lines + includes(incFileContents, incPath)
            else:
                print("Filename not quoted:", Line(contents, i, rootFilePath))
                exit()
        else:
            lines.append(Line(contents, i, rootFilePath))
    # print("\n".join([str(x) for x in lines]))
    return lines


def tokenize(fileContents: str, filePath: Path) -> list[Token]:
    return context(split(includes(fileContents, filePath)))


if __name__ == "__main__":
    file = Path("test.g")
    with open(file, "r") as f:
        fileContents: str = f.read()

    tokens: list[Token] = tokenize(fileContents, file)

    for t in tokens:
        t.blame()
