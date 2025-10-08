from typing import Optional

from pydantic import BaseModel, Field, ValidationError


class JsonProviderError(Exception):
    """A custom exception to represent unknown errors, with support for chaining exceptions."""

    def __init__(self, message_or_exception: str | Exception):
        """
        Initialize the JsonProviderError.

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
            return f"JsonProviderError: {self.message} (caused by {type(self.original_exception).__name__})"
        return f"JsonProviderError: {self.message}"


class ResponseValidationError(JsonProviderError):
    def __init__(self, message_or_exception: str | ValidationError):
        super().__init__(message_or_exception)

    def __str__(self):
        """
        Return a string representation of the error.

        If the error wraps another exception, include its type in the output.
        """
        if self.original_exception:
            return f"ResponseValidationError: {self.message} (caused by {type(self.original_exception).__name__})"
        return f"ResponseValidationError: {self.message}"


class JsonRpcErrorModel(BaseModel):
    code: int
    message: str
    data: Optional[dict] = Field(default=None)


class JsonRpcError(JsonProviderError):
    error: JsonRpcErrorModel

    def __init__(self, error: JsonRpcErrorModel):
        self.error = error
        super().__init__(self.error.message)

    def __str__(self):
        """
        Return a string representation of the error.

        If the error wraps another exception, include its type in the output.
        """
        return f"JsonRpcError: {self.error.message}"
