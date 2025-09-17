from semantic_pass import Symbol
from silenterror import SilentException


class SemanticError(SilentException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class SyntaxError(SemanticError):
    def __init__(self, token: Symbol | None, message: str):
        # if token is None:
        #     message = "Syntax error: " + message + "\n" + "Failed to blame"
        # else:
        #     message = (
        #         "Syntax error: " + message + "\n" + "\n".join(token.blame_string())
        #     )
        super().__init__(message)
