from typing import ClassVar, List, Optional, Tuple

from pydantic import BaseModel

from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.list_struct import ListStruct, deserialize_list
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Codec, Int, Seder


# analog: OutputOwners
class Secp256k1OutputOwners(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.OutputOwners

    locktime: Long
    threshold: Int
    addresses: ListStruct[Address]

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Secp256k1OutputOwners", bytes]:
        (locktime, data) = Long.deserialize(data, codec)
        (threshold, data) = Int.deserialize(data, codec)
        (addresses, data) = deserialize_list(Address, data, codec)

        return (
            Secp256k1OutputOwners(
                locktime=locktime,
                threshold=threshold,
                addresses=addresses,
            ),
            data,
        )

    def serialize(self, codec: Codec) -> bytes:
        data = self.locktime.serialize(codec)
        data += self.threshold.serialize(codec)
        data += self.addresses.serialize(codec)

        return data

    def match_owners(self, addresses: List[Address], min_issuance_time: int) -> Optional[List[int]]:
        if self.locktime.value > min_issuance_time:
            return None

        sigs = []
        addresses_set = set(addresses)
        for i, owner_addr in enumerate(self.addresses.list):
            if owner_addr not in addresses_set:
                continue

            sigs.append(i)

        if len(sigs) != self.threshold.value:
            return None
        return sigs
