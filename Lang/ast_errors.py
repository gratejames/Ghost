from my_ast import Token
import sys
from silenterror import SilentException


class CompilerError(SilentException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class SyntaxError(CompilerError):
    def __init__(self, token: Token | None, message: str):
        if token is None:
            message = "Syntax error: " + message + "\n" + "Failed to blame"
        else:
            message = (
                "Syntax error: " + message + "\n" + "\n".join(token.blame_string())
            )
        super().__init__(message)


class Expected(SyntaxError):
    def __init__(self, token: Token | None, what_expected: str):
        message = f"Expected {what_expected}"
        super().__init__(token, message)
