from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.list_struct import ListStruct, deserialize_list
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Codec, Int, Seder


class Secp256k1TransferInput(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.TransferInput

    amount: Long
    address_indices: ListStruct[Int]

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Secp256k1TransferInput", bytes]:
        (amount, data) = Long.deserialize(data, codec)
        (address_indices, data) = deserialize_list(Int, data, codec)

        return Secp256k1TransferInput(amount=amount, address_indices=address_indices), data

    def serialize(self, codec: Codec):
        data = self.amount.serialize(codec)
        data += self.address_indices.serialize(codec)

        return data
