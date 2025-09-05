from my_ast import Token


class SilentException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class SyntaxError(SilentException):
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


import sys


# Custom exception hook
def handle_uncaught(exc_type, exc_value, traceback):
    if isinstance(exc_value, SilentException):
        print(exc_value.message)
        sys.exit(1)
    else:
        # Default behavior for other exceptions
        sys.__excepthook__(exc_type, exc_value, traceback)


# Set the global exception hook
sys.excepthook = handle_uncaught
