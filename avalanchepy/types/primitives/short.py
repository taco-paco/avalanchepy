from typing import Tuple

from pydantic import BaseModel, Field

from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.seder import Codec, Seder

SHORT_LEN = 2


class Short(BaseModel, Seder):
    _type = TypeSymbols.Short
    value: int = Field(ge=0, lt=2 ** (8 * SHORT_LEN))

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Short", bytes]:
        if len(data) < SHORT_LEN:
            raise DeserializationError.invalid_size(len(data), SHORT_LEN)

        value = int.from_bytes(data[0:SHORT_LEN], byteorder="big")
        return Short(value=value), data[SHORT_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return self.value.to_bytes(SHORT_LEN, byteorder="big")
