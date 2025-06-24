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
]
assignment = [
    "=",
    "+=",
    "-=",
    "*=",
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


class pre_token:
    def __init__(self, contents: str = "", line: int = 0, file: Path = Path()):
        self.contents = contents
        self.line = line
        self.file = file

    def __repr__(self):
        return f"('{self.contents}':{self.line})"

    contents: str = ""
    line: int = 0
    file: Path


class token:
    def __init__(
        self, type: str, contents: str | int, tokenNumber: int, line: int, file: Path
    ):
        self.type = type
        self.contents = contents
        self.tokenNumber = tokenNumber
        self.line = line
        self.file = file

    def __repr__(self):
        return f"({self.type} '{self.contents}', {self.line}:{self.tokenNumber})"

    type: str = ""
    contents: str | int = ""
    tokenNumber: int = 0
    line: int = 0
    file: Path


def split(fileLines: list[Line]) -> list[pre_token]:
    contents: list[pre_token] = []
    # line_number: int = 1
    for line in fileLines:
        for char in line.contents:
            if char == "/" and len(contents) > 0 and contents[-1].contents == "/":
                contents = contents[:-1]
                break
            if not (char == " " and contents[-1].contents == " ") and not char == "\n":
                contents.append(pre_token(char, line.line, line.file))
        contents.append(pre_token(" ", line.line, line.file))
    # print(contents)

    tokens: list[pre_token] = [pre_token("", 1)]
    stringMode: bool = False

    for i, charPair in enumerate(contents):
        char = charPair.contents
        if stringMode:
            if char == '"':
                stringMode = False
                tokens[-1].contents += '"'
                tokens[-1].line = charPair.line
                tokens.append(pre_token("", 0))
            else:
                tokens[-1].contents += char
        elif char.strip() == "":
            if tokens[-1].contents != "":
                tokens.append(pre_token("", 0))
        elif char == '"':
            if tokens[-1].contents == "":
                tokens.pop(-1)
            tokens.append(pre_token('"', charPair.line))
            stringMode = True
        elif char in "()`~!@#$%^&*()-+=[]\\{}|;:,./?><'":
            if (
                char == "="
                and len(tokens) > 1
                and tokens[-1].contents
                in ["=", "<", ">", "!", "+", "-", "&", "^", "|", "<<", ">>", "*"]
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
            else:
                tokens.append(pre_token(char, charPair.line))
        else:
            if (
                tokens[-1].contents == ""
                or tokens[-1].contents.replace("_", "").isalnum()
            ):
                tokens[-1].contents += char
                tokens[-1].line = charPair.line
            else:
                tokens.append(pre_token(char, charPair.line))

    if tokens[-1].contents == "":
        tokens = tokens[:-1]
    return tokens


def context(c: list[pre_token]) -> list[token]:
    tokens = []
    for tokenI, item in enumerate(c):
        # item, line_number = item.contents, item.line
        if item.contents in types:
            tokens.append(token("type", item.contents, tokenI, item.line, item.file))
        elif item.contents in keywords:
            tokens.append(token("keyword", item.contents, tokenI, item.line, item.file))
        elif item.contents in operators:
            tokens.append(
                token("operator", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents in symbols:
            tokens.append(token("symbol", item.contents, tokenI, item.line, item.file))
        elif item.contents.isdigit():
            tokens.append(
                token(
                    "literal integer", int(item.contents), tokenI, item.line, item.file
                )
            )
        elif (
            len(item.contents) > 3
            and item.contents[0] == '"'
            and item.contents[-1] == '"'
        ):
            tokens.append(
                token(
                    "literal string", item.contents[1:-1], tokenI, item.line, item.file
                )
            )
        elif (
            len(item.contents) > 2
            and item.contents[0] == "0"
            and item.contents[1] in "bx"
        ):
            tokens.append(
                token(
                    "literal integer",
                    int(item.contents, 0),
                    tokenI,
                    item.line,
                    item.file,
                )
            )
        elif item.contents == "(":
            tokens.append(
                token("open paren", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents == ")":
            tokens.append(
                token("close paren", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents == "[":
            tokens.append(
                token("open bracket", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents == "]":
            tokens.append(
                token("close bracket", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents == "{":
            tokens.append(
                token("open brace", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents == "}":
            tokens.append(
                token("close brace", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents == "'":
            tokens.append(
                token("single quote", item.contents, tokenI, item.line, item.file)
            )
        elif item == '"':
            tokens.append(
                token("double quote", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents == ",":
            tokens.append(token("comma", item.contents, tokenI, item.line, item.file))
        elif item.contents == ";":
            tokens.append(
                token("semicolon", item.contents, tokenI, item.line, item.file)
            )
        elif item.contents in assignment:
            tokens.append(
                token("assignment", item.contents, tokenI, item.line, item.file)
            )
        # elif item.contents == "asm":
        #     tokens.append(
        #         token("asm",)
        #     )
        else:
            tokens.append(
                token("identifier", item.contents, tokenI, item.line, item.file)
            )
    return tokens


def includes(fileContents: str, filePath: Path) -> list[Line]:
    lines: list[Line] = []
    for i, contents in enumerate(fileContents.split("\n")):
        if contents.startswith("#include "):
            fileName = contents.replace("#include ", "", 1).strip()
            if filePath.suffix not in ["g"]:
                lines.append(Line(contents, i, filePath))
                continue

            if fileName[0] == '"' and fileName[-1] == '"':
                incPath = filePath.parent.absolute() / fileName[1:-1]
                with open(incPath, "r") as f:
                    incFileContents = f.read()
                lines = lines + includes(incFileContents, incPath)
            else:
                print("Filename not quoted:", Line(contents, i, filePath))
                exit()
        else:
            lines.append(Line(contents, i, filePath))
    # print("\n".join([str(x) for x in lines]))
    return lines


def tokenize(fileContents: str, filePath: Path) -> list[token]:
    return context(split(includes(fileContents, filePath)))


if __name__ == "__main__":
    file = Path("test.g")
    with open(file, "r") as f:
        fileContents: str = f.read()

    tokens: list[token] = tokenize(fileContents, file)

    print(tokens)
