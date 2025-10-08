from typing import Optional, Type, TypeVar

from pydantic import BaseModel

from avalanchepy.clients.errors import ClientError, FormatError, ServerError
from avalanchepy.json_provider.errors import (
    JsonProviderError,
    JsonRpcError,
    ResponseValidationError,
)
from avalanchepy.json_provider.json_provider import JsonProvider

T = TypeVar("T", bound=BaseModel)


class BaseClient:
    url: str
    path: str
    json_provider: JsonProvider

    def __init__(self, url: str, path: str):
        self.url = url
        self.path = path
        self.json_provider = JsonProvider(url + path)

    def _wrapped_call(self, result_type: Type[T], method: str, parameters: Optional[BaseModel] = None) -> T:
        # Convert to client level exception
        try:
            return self.json_provider.call_method(result_type, method, parameters)
        except JsonRpcError as e:
            raise ServerError(e) from e
        except ResponseValidationError as e:
            raise FormatError(e) from e
        except JsonProviderError as e:
            raise ClientError(e) from e
