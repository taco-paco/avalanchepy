from pydantic import ValidationError

from avalanchepy.json_provider.errors import (
    JsonProviderError,
    JsonRpcError,
    ResponseValidationError,
)
from avalanchepy.types.errors import DeserializationError


class ServerError(Exception):
    def __init__(self, error: JsonRpcError):
        """
        Initialize the ServerError exception.

        :param error: The original exception, if any, that caused this error.
        """
        self.error = error
        super().__init__(error)

    def __str__(self):
        """
        Return a string representation of the error.

        Include the type and message of the wrapped exception in the output.
        """
        return f"ServerError Caused by: {type(self.error).__name__} - {self.error}"


class ClientError(Exception):
    def __init__(self, error: JsonProviderError):
        """
        Initialize the ClientError exception.

        :param error: The original exception, if any, that caused this error.
        """
        self.error = error
        super().__init__(error)

    def __str__(self):
        """
        Return a string representation of the error.

        Include the type and message of the wrapped exception in the output.
        """
        return f"ClientError Caused by: {type(self.error).__name__} - {self.error}"


class FormatError(Exception):
    def __init__(self, error: ValidationError | ResponseValidationError | DeserializationError):
        """
        Initialize the FormatError exception.

        :param error: The original exception, if any, that caused this error.
        """
        self.error = error
        super().__init__(error)

    def __str__(self):
        """
        Return a string representation of the error.

        Include the type and message of the wrapped exception in the output.
        """
        return f"FormatError Caused by: {type(self.error).__name__} - {self.error}"
