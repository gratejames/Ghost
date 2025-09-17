import sys


class SilentException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def handle_uncaught(exc_type, exc_value, traceback):
    if isinstance(exc_value, SilentException):
        print(exc_value.message)
        sys.exit(1)
    # elif
    else:
        # Default behavior for other exceptions
        sys.__excepthook__(exc_type, exc_value, traceback)


# # Set the global exception hook
sys.excepthook = handle_uncaught
