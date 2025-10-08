from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.primitives.byte import Byte
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.list_struct import ListStruct, deserialize_list
from avalanchepy.types.seder import Codec, Int, Seder


class BaseTx(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.BaseTx

    network_id: Int
    blockchain_id: Id
    outputs: ListStruct[TransferableOutput]
    inputs: ListStruct[TransferableInput]
    memo: ListStruct[Byte]

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["BaseTx", bytes]:
        (network_id, data) = Int.deserialize(data, codec)
        (blockchain_id, data) = Id.deserialize(data, codec)
        (outputs, data) = deserialize_list(TransferableOutput, data, codec)
        (inputs, data) = deserialize_list(TransferableInput, data, codec)
        (memo, data) = deserialize_list(Byte, data, codec)

        base_tx = BaseTx(network_id=network_id, blockchain_id=blockchain_id, outputs=outputs, inputs=inputs, memo=memo)
        return base_tx, data

    def serialize(self, codec: Codec) -> bytes:
        data = self.network_id.serialize(codec)
        data += self.blockchain_id.serialize(codec)
        data += self.outputs.serialize(codec)
        data += self.inputs.serialize(codec)
        data += self.memo.serialize(codec)

        return data
