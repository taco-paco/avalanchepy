from typing import Annotated, ClassVar, Tuple

import base58
from pydantic import AfterValidator, BaseModel, ConfigDict, model_serializer

from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.utils import Base58Check, validate_bytes_length
from avalanchepy.types.seder import Codec, Seder

NODE_ID_LEN = 20
NODE_ID_SEP = "-"
NODE_ID_PREFIX = "NodeID"


class NodeId(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.NodeId
    model_config = ConfigDict(ignored_types=(Seder,))

    value: Annotated[bytes, AfterValidator(lambda x: validate_bytes_length(x, NODE_ID_LEN))]

    @model_serializer(return_type=str)
    def model_serialize(self) -> str:
        return self.to_json()

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["NodeId", bytes]:
        if len(data) < NODE_ID_LEN:
            raise DeserializationError.invalid_size(len(data), NODE_ID_LEN)

        return NodeId(value=data[0:NODE_ID_LEN]), data[NODE_ID_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return self.value

    @staticmethod
    def from_string(data: str) -> "NodeId":
        parts = data.split(NODE_ID_SEP, 2)
        if len(parts) != 2:
            raise ValueError(f"Invalid node id format: {data}")
        if parts[0] != NODE_ID_PREFIX:
            raise ValueError(f"Invalid node id prefix: {NODE_ID_PREFIX}")

        raw = base58.b58decode(parts[1])[:-4]
        return NodeId(value=raw)

    def to_json(self) -> str:
        return f"{NODE_ID_PREFIX}{NODE_ID_SEP}{Base58Check.encode(self.value)}"

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
        if not isinstance(other, NodeId):
            return False
        return self.value == other.value
