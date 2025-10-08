from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Codec, Seder


# TODO: rename to StakeableLockedOutput. skipped
class StakeableLockOut(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.StakeableLockOut

    locktime: Long
    transferable_output: Secp256k1TransferOutput

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["StakeableLockOut", bytes]:
        (locktime, data) = Long.deserialize(data, codec)
        (transferable_output, data) = codec.unpack_prefix(data)
        assert isinstance(transferable_output, Secp256k1TransferOutput)

        return StakeableLockOut(locktime=locktime, transferable_output=transferable_output), data

    def serialize(self, codec: Codec) -> bytes:
        data = self.locktime.serialize(codec)
        data += codec.pack_prefix(self.transferable_output)

        return data
