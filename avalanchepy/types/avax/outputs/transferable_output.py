from typing import ClassVar, Tuple, Union

from pydantic import BaseModel

from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Codec, Seder


class TransferableOutput(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.TransferOutput

    asset_id: Id
    output: Union[Secp256k1TransferOutput, StakeableLockOut]

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["TransferableOutput", bytes]:
        (asset_id, data) = Id.deserialize(data, codec)
        (output, data) = codec.unpack_prefix(data)
        assert isinstance(output, Union[Secp256k1TransferOutput, StakeableLockOut])

        return TransferableOutput(asset_id=asset_id, output=output), data

    def serialize(self, codec: Codec) -> bytes:
        data = self.asset_id.serialize(codec)
        data += codec.pack_prefix(self.output)

        return data

    def amount(self) -> Long:
        if isinstance(self.output, Secp256k1TransferOutput):
            return self.output.amount
        else:
            return self.output.transferable_output.amount

    def output_owners(self) -> Secp256k1OutputOwners:
        if isinstance(self.output, Secp256k1TransferOutput):
            return self.output.output_owners
        else:
            return self.output.transferable_output.output_owners
