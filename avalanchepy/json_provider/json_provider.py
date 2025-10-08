import json
from typing import Generic, Optional, Type, TypeVar

import requests
from pydantic import BaseModel, Field, ValidationError, model_validator

from avalanchepy.json_provider.errors import (
    JsonProviderError,
    JsonRpcError,
    JsonRpcErrorModel,
    ResponseValidationError,
)

T = TypeVar("T", bound=BaseModel)


class JsonRpcResponse(BaseModel, Generic[T]):
    jsonrpc: str
    result: Optional[T] = Field(default=None)
    id: int
    error: Optional[JsonRpcErrorModel] = Field(default=None)

    @model_validator(mode="after")
    def validate_result_error(self):
        if self.result is None and self.error is None:
            raise ValueError("Response must contain either result or error")

        if self.result is not None and self.error is not None:
            raise ValueError("Response must contain either result or error, but not both")

        return self


class JsonProvider:
    url: str
    req_id: int

    def __init__(self, url: str):
        self.url = url
        self.req_id = 0

    def call_method(
        self,
        result_type: Type[T],
        method: str,
        parameters: Optional[BaseModel] = None,
    ) -> T:
        headers = {"Content-Type": "application/json"}
        body = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": method,
            "params": {} if parameters is None else parameters.model_dump(by_alias=True),
        }

        try:
            self.req_id += 1

            response = requests.post(
                self.url,
                data=json.dumps(body),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise JsonProviderError(e) from e

        try:
            json_response = JsonRpcResponse[result_type](**data)
        except ValidationError as e:
            raise ResponseValidationError(e) from e

        if json_response.error is not None:
            raise JsonRpcError(json_response.error)

        return json_response.result
