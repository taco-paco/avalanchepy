from typing import Annotated, ClassVar, Tuple

from pydantic import AfterValidator, BaseModel, ConfigDict, model_serializer

from avalanchepy.types.errors import DeserializationError, SerializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.utils import (
    decode_bech32_to_bytes,
    encode_bech32_to_str,
    validate_bytes_length,
)
from avalanchepy.types.seder import Codec, Seder

ADDRESS_LEN = 20
ADDRESS_SEP = "-"


class Address(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.Address
    model_config = ConfigDict(ignored_types=(Seder,))

    value: Annotated[bytes, AfterValidator(lambda x: validate_bytes_length(x, ADDRESS_LEN))]

    @model_serializer(return_type=str)
    def model_serialize(self) -> str:
        return self.to_json()

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Address", bytes]:
        if len(data) < ADDRESS_LEN:
            raise DeserializationError.invalid_size(len(data), ADDRESS_LEN)

        return Address(value=data[0:ADDRESS_LEN]), data[ADDRESS_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return self.value

    def to_json(self, chain_id="P", hrp="fuji") -> str:
        return self.to_string(chain_id, hrp)

    def to_string(self, chain_id: str, hrp: str) -> str:
        try:
            bech32_encoded_address = encode_bech32_to_str(hrp, self.value)
        except Exception:
            raise SerializationError("Failed to bech32 encode address")

        return f"{chain_id}{ADDRESS_SEP}{bech32_encoded_address}"

    @staticmethod
    def from_string(data: str) -> "Address":
        parts = data.split(ADDRESS_SEP, 2)
        if len(parts) != 2:
            raise DeserializationError(f"Invalid address format: {data}")

        try:
            _, addr = decode_bech32_to_bytes(parts[1])
        except Exception:
            raise DeserializationError(f"Failed to decode with bech32: {data}")

        return Address(value=addr)

    # Implement __hash__ to make the object hashable
    def __hash__(self):
        """
        Compute the hash value for the Address object.

        Returns:
            int: The hash value of the Address object.
        """
        return hash(self.value)  # Hash based on the 'value' field

    # Implement __eq__ to define equality for dictionary keys
    def __eq__(self, other):
        """
        Compare two Address objects for equality.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if the other object is an Address with the same value, False otherwise.
        """
        if not isinstance(other, Address):
            return False
        return self.value == other.value


ADDRESS_EMPTY = Address(value=bytes(ADDRESS_LEN * [0]))
