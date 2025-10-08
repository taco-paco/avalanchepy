from typing import ClassVar, Tuple, Union

from pydantic import BaseModel

from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.avax.utxoid import UtxoId
from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.seder import Codec, Seder


class Utxo(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.UTXO

    utxo_id: UtxoId
    asset_id: Id
    output: Union[Secp256k1OutputOwners, Secp256k1TransferOutput, StakeableLockOut]

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Utxo", bytes]:
        (utxo_id, data) = UtxoId.deserialize(data, codec)
        (asset_id, data) = Id.deserialize(data, codec)
        (output, data) = codec.unpack_prefix(data)

        if isinstance(output, Union[Secp256k1OutputOwners, Secp256k1TransferOutput, StakeableLockOut]) is False:
            raise DeserializationError(f"Invalid output type: {output._type}")

        return Utxo(utxo_id=utxo_id, asset_id=asset_id, output=output), data

    def serialize(self, codec: Codec) -> bytes:
        data = self.utxo_id.serialize(codec)
        data += self.asset_id.serialize(codec)
        data += codec.pack_prefix(self.output)

        return data

    def get_output_owners(self) -> Secp256k1OutputOwners:
        if isinstance(self.output, Secp256k1TransferOutput):
            return self.output.output_owners
        elif isinstance(self.output, StakeableLockOut):
            return self.transferable_output.output_owners
        else:
            return self.output
