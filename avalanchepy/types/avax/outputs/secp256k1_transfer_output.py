from typing import ClassVar, List, Optional, Tuple

from pydantic import BaseModel

from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Codec, Seder


# analog: TransferOutput.ts
class Secp256k1TransferOutput(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.TransferOutput

    amount: Long
    output_owners: Secp256k1OutputOwners

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Secp256k1TransferOutput", bytes]:
        (amount, data) = Long.deserialize(data, codec)
        (output_owners, data) = Secp256k1OutputOwners.deserialize(data, codec)

        return (
            Secp256k1TransferOutput(amount=amount, output_owners=output_owners),
            data,
        )

    def serialize(self, codec: Codec) -> bytes:
        data = self.amount.serialize(codec)
        data += self.output_owners.serialize(codec)

        return data

    def match_owners(self, addresses: List[Address], min_issuance_time: int) -> Optional[List[int]]:
        return self.output_owners.match_owners(addresses, min_issuance_time)
