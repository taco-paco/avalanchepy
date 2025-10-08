from typing import ClassVar, List, Tuple

from pydantic import BaseModel

from avalanchepy.types.avax.base_tx import BaseTx
from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.avax.subnet_validator import SubnetValidator
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.list_struct import ListStruct, deserialize_list
from avalanchepy.types.seder import Codec, Seder
from avalanchepy.types.signable import Signable


# TODO: make type utf-8 compatible for json representation
class AddPermissionlessDelegatorTx(BaseModel, Seder, Signable):
    _type: ClassVar[TypeSymbols] = TypeSymbols.AddPermissionlessDelegatorTx

    base_tx: BaseTx
    subnet_validator: SubnetValidator
    stake_outputs: ListStruct[TransferableOutput]
    delegator_rewards_owner: Secp256k1OutputOwners

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["BaseTx", bytes]:
        (base_tx, data) = BaseTx.deserialize(data, codec)
        (subnet_validator, data) = SubnetValidator.deserialize(data, codec)
        (stake_outputs, data) = deserialize_list(TransferableOutput, data, codec)

        (delegator_rewards_owner, data) = codec.unpack_prefix(data)
        assert isinstance(delegator_rewards_owner, Secp256k1OutputOwners)

        tx = AddPermissionlessDelegatorTx(
            base_tx=base_tx,
            subnet_validator=subnet_validator,
            stake_outputs=stake_outputs,
            delegator_rewards_owner=delegator_rewards_owner,
        )
        return tx, data

    def serialize(self, codec: Codec) -> bytes:
        data = self.base_tx.serialize(codec)
        data += self.subnet_validator.serialize(codec)
        data += self.stake_outputs.serialize(codec)
        data += codec.pack_prefix(self.delegator_rewards_owner)

        return data

    def get_signers(self, input_utxos: List[Utxo]) -> List[List[Address]]:
        return Signable.extract_signers(input_utxos, self.base_tx.inputs.list)
