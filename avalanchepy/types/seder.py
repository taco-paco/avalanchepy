from __future__ import annotations

from typing import ClassVar, Dict, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, Field, model_serializer

from avalanchepy.types.errors import DeserializationError, SerializationError
from avalanchepy.types.primitives.constants import TypeSymbols


class Serializable:
    _type: ClassVar[TypeSymbols]

    def serialize(self, codec: Codec) -> bytes:
        raise NotImplementedError()


class Deserializable:
    @staticmethod
    def deserialize(data: bytes, codec: Codec):
        raise NotImplementedError()


class Seder(Serializable, Deserializable):
    pass


T = TypeVar("T", bound=Serializable)


class Codec(Seder):
    _type = TypeSymbols.Codec
    type_id_to_type: List[Optional[Seder]]
    type_to_type_id: Dict[TypeSymbols, int]

    def __init__(self, type_id_to_type: List[Optional[Seder]]):
        self.type_id_to_type = type_id_to_type
        self.type_to_type_id = {}

        for i, value in enumerate(type_id_to_type):
            if value is None:
                continue

            self.type_to_type_id[value._type.value] = i

    def pack_prefix(self, ser: T) -> bytes:
        if ser._type not in self.type_to_type_id:
            raise SerializationError(f"TypeSymbol: {ser._type} id doesn't exist.")

        type_id = self.type_to_type_id[ser._type]
        prefix = Int(value=type_id).serialize(self)
        data = ser.serialize(self)

        return prefix + data

    def unpack_prefix(self, buf: bytes) -> (T, bytes):
        (type_id, buf) = unpack(buf, Int, self)
        if type_id.value >= len(self.type_id_to_type) or type_id.value < 0:
            raise DeserializationError(f"Invalid typeId: {type_id.value}")

        type = self.type_id_to_type[type_id.value]
        if type is None:
            raise DeserializationError(f"Can't find type for typeId: {type_id}")

        (object, rest) = type.deserialize(buf, self)
        return (object, rest)

    def serialize(self, codec: Codec) -> bytes:
        raise NotImplementedError("not implemented")

    @staticmethod
    def deserialize(data: bytes, codec: "Codec"):
        return codec.unpack_prefix(data)


D = TypeVar("D", bound=Deserializable)


def unpack(
    buffer: bytes,
    de: Type[D],
    codec: Optional[Codec],
) -> Tuple[D, bytes]:
    if len(buffer) == 0:
        raise ValueError("Empty buffer")

    (res, buffer) = de.deserialize(buffer, codec)
    return res, buffer


INT_LEN = 4


class Int(BaseModel, Seder):
    _type = TypeSymbols.Int
    value: int = Field(ge=0, lt=2 ** (8 * INT_LEN))

    @model_serializer(return_type=int)
    def model_serialize(self) -> int:
        return self.value

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> ["Int", bytes]:
        if len(data) < INT_LEN:
            raise DeserializationError.invalid_size(len(data), INT_LEN)

        value = int.from_bytes(data[0:INT_LEN], byteorder="big")
        return Int(value=value), data[INT_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return self.value.to_bytes(INT_LEN, byteorder="big")
