import hashlib
from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.seder import INT_LEN, Codec, Int, Seder, unpack


class UtxoId(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.UTXOID

    id: Id
    output_idx: Int

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["UtxoId", bytes]:
        (id, data) = unpack(data, Id, codec)
        (number, data) = unpack(data, Int, codec)

        return UtxoId(id=id, output_idx=number), data

    def serialize(self, codec: Codec) -> bytes:
        data = self.id.serialize(codec)
        data += self.output_idx.serialize(codec)

        return data

    def input_id(self) -> Id:
        output_idx_bytes = int.to_bytes(self.output_idx.value, length=INT_LEN, byteorder="big", signed=False)
        buf = output_idx_bytes + self.id.value

        digest = hashlib.sha256(buf).digest()
        return Id(value=digest)

    def __eq__(self, other: "UtxoId") -> bool:
        """
        Compare two UtxoId objects for equality.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if the other object is an UtxoId with the same value, False otherwise.
        """
        if not isinstance(other, UtxoId):
            return NotImplemented
        return self.id == other.id and self.output_idx == other.output_idx

    def __lt__(self, other: "UtxoId") -> bool:
        """
        Define how UtxoId instances should be compared for sorting.

        Args:
            other (UtxoId): The other UtxoId to compare with.

        Returns:
            bool: True if this instance is less than the other, False otherwise.
        """
        if not isinstance(other, UtxoId):
            return NotImplemented
        if self.id < other.id:
            return True
        if self.id > other.id:
            return False
        return self.output_idx.value < other.output_idx.value
