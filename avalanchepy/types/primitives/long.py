from typing import Tuple

from pydantic import BaseModel, Field, model_serializer

from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.seder import Codec, Seder

LONG_LEN = 8


# analog: bigintptr.ts
class Long(BaseModel, Seder):
    _type = TypeSymbols.BigIntPr
    value: int = Field(ge=0, lt=2 ** (8 * LONG_LEN))

    @model_serializer(return_type=str)
    def model_serialize(self) -> str:
        return self.to_json()

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Long", bytes]:
        if len(data) < LONG_LEN:
            raise DeserializationError.invalid_size(len(data), LONG_LEN)

        value = int.from_bytes(data[0:LONG_LEN], byteorder="big")
        return Long(value=value), data[LONG_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return self.value.to_bytes(LONG_LEN, byteorder="big")

    def to_json(self) -> str:
        return str(self.value)

    def __eq__(self, other: "Long"):
        """
        Compare two Long objects for equality.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if the other object is an Long with the same value, False otherwise.
        """
        if not isinstance(other, Long):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: "Long") -> bool:
        """
        Define how Long instances should be compared for sorting.

        Args:
            other (Long): The other Long to compare with.

        Returns:
            bool: True if this instance is less than the other, False otherwise.
        """
        if not isinstance(other, Long):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other: "Long") -> bool:
        """
        Define how Long instances should be compared for less than or equal to.

        Args:
            other (Long): The other Long to compare with.

        Returns:
            bool: True if this instance is less than or equal to the other, False otherwise.
        """
        if not isinstance(other, Long):
            return NotImplemented
        return self.value <= other.value

    def __sub__(self, other: "Long") -> "Long":
        """
        Subtract the value of another Long instance from this instance.

        Args:
            other (Long): The Long instance to subtract.

        Returns:
            Long: A new Long instance with the result of the subtraction.
        """
        return Long(value=self.value - other.value)

    def __add__(self, other: "Long") -> "Long":
        """
        Add the value of another Long instance to this instance.

        Args:
            other (Long): The Long instance to add.

        Returns:
            Long: A new Long instance with the result of the addition.
        """
        return Long(value=self.value + other.value)
