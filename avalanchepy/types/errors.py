class SederError(Exception):
    """A custom exception to represent unknown errors, with support for chaining exceptions."""

    def __init__(self, message_or_exception: str | Exception):
        """
        Initialize the SederError.

        Args:
            message_or_exception (str | Exception): The error message or an original exception.
        """
        if isinstance(message_or_exception, Exception):
            self.original_exception = message_or_exception
            self.message = str(message_or_exception)
        else:
            self.original_exception = None
            self.message = message_or_exception

        super().__init__(self.message)

    def __str__(self):
        """
        Return a string representation of the error.

        If the error wraps another exception, include its type in the output.
        """
        if self.original_exception:
            return f"SederError: {self.message} (caused by {type(self.original_exception).__name__})"
        return f"SederError: {self.message}"


class DeserializationError(SederError):
    def __init__(self, message_or_exception):
        super().__init__(message_or_exception)

    @staticmethod
    def invalid_size(actual: int, expected: int) -> "DeserializationError":
        return DeserializationError(f"Invalid data size. expected {expected}, actual: {actual}")

    def __str__(self):
        """
        Return a string representation of the error.

        If the error wraps another exception, include its type in the output.
        """
        if self.original_exception:
            return f"DeserializationError: {self.message} (caused by {type(self.original_exception).__name__})"
        return f"DeserializationError: {self.message}"


class SerializationError(SederError):
    def __init__(self, message_or_exception):
        super().__init__(message_or_exception)

    def __str__(self):
        """
        Return a string representation of the error.

        If the error wraps another exception, include its type in the output.
        """
        if self.original_exception:
            return f"SerializationError: {self.message} (caused by {type(self.original_exception).__name__})"
        return f"SerializationError: {self.message}"
