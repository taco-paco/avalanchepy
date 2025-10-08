from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.avax.inputs.secp256k1_transfer_input import (
    Secp256k1TransferInput,
)
from avalanchepy.types.avax.utxoid import UtxoId
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Codec, Seder


class TransferableInput(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.TransferInput

    utxo_id: UtxoId
    asset_id: Id
    # can be StakeableLockIn
    input: Secp256k1TransferInput

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["TransferableInput", bytes]:
        (utxo_id, data) = UtxoId.deserialize(data, codec)
        (asset_id, data) = Id.deserialize(data, codec)
        (input, data) = codec.unpack_prefix(data)

        assert isinstance(input, Secp256k1TransferInput)
        return TransferableInput(utxo_id=utxo_id, asset_id=asset_id, input=input), data

    def serialize(self, codec: Codec) -> bytes:
        data = self.utxo_id.serialize(codec)
        data += self.asset_id.serialize(codec)
        data += codec.pack_prefix(self.input)

        return data

    def amount(self) -> Long:
        return self.input.amount
