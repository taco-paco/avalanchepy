from typing import Annotated, ClassVar, Tuple

from pydantic import AfterValidator, BaseModel, model_serializer

from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.utils import (
    Base58Check,
    pad_left,
    validate_bytes_length,
)
from avalanchepy.types.seder import Codec, Seder

ID_LEN = 32


class Id(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.Id
    value: Annotated[bytes, AfterValidator(lambda x: validate_bytes_length(x, ID_LEN))]

    @model_serializer(return_type=str)
    def model_serialize(self) -> str:
        return self.to_json()

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Id", bytes]:
        if len(data) < ID_LEN:
            raise DeserializationError.invalid_size(len(data), ID_LEN)

        return Id(value=data[:ID_LEN]), data[ID_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return pad_left(self.value, ID_LEN)

    @staticmethod
    def from_string(value: str) -> "Id":
        raw = Base58Check.decode(value)
        return Id(value=raw)

    def to_string(self) -> str:
        return Base58Check.encode(self.value)

    def to_json(self) -> str:
        return self.to_string()

    def __hash__(self):
        """
        Compute the hash value for the Id object.

        Returns:
            int: The hash value of the Id object.
        """
        return hash(self.value)  # Hash based on the 'value' field

    def __eq__(self, other):
        """
        Compare two Id objects for equality.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if the other object is an Id with the same value, False otherwise.
        """
        if not isinstance(other, Id):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: "Id") -> bool:
        """
        Define how Id instances should be compared for sorting.

        Args:
            other (Id): The other Id to compare with.

        Returns:
            bool: True if this instance is less than the other, False otherwise.
        """
        if not isinstance(other, Id):
            return NotImplemented
        return self.value < other.value
