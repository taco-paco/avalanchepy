from typing import ClassVar, Tuple

from pydantic import BaseModel, Field, model_serializer

from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.seder import Codec, Seder

BYTE_LEN = 1


class Byte(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.Byte
    value: int = Field(ge=0, lt=256)

    @model_serializer(return_type=str)
    def model_serialize(self) -> str:
        return self.to_json()

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Byte", bytes]:
        if len(data) == 0:
            raise DeserializationError.invalid_size(1, 0)

        return Byte(value=int.from_bytes(data[:BYTE_LEN], byteorder="big", signed=False)), data[BYTE_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return self.value.to_bytes(BYTE_LEN, byteorder="big")

    def to_json(self) -> str:
        return f"0x{self.value:02x}"
