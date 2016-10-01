class TnyBotException(Exception):
    """Base extension class for this Library."""
    pass


class SameUserException(TnyBotException):
    """Exception that is thrown when the bot tries to respond to it's own messages."""

    def __init__(self):
        message = "The bot is responding to it's own messages. This may cause and infinite loop."
        super(SameUserException, self).__init__(message)
