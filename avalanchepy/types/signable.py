from typing import Dict, List

from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.primitives.address import ADDRESS_EMPTY, Address
from avalanchepy.types.primitives.id import Id


class Signable:
    def get_signers(self, input_utxos: List[Utxo]) -> List[Address]:
        raise NotImplementedError("Signeable.get_signers() is not implemented")

    @staticmethod
    def extract_signers(input_utxos: List[Utxo], transferable_inputs: List[TransferableInput]) -> List[List[Address]]:
        inputs_signers: List[List[Address]] = len(transferable_inputs) * [[]]
        utxo_dict: Dict[Id, Utxo] = {utxo.utxo_id.input_id(): utxo for utxo in input_utxos}
        for i, transferable_input in enumerate(transferable_inputs):
            input_id = transferable_input.utxo_id.input_id()
            if input_id not in utxo_dict:
                raise KeyError(f"UTXO with input_id {input_id} not found")

            utxo = utxo_dict[input_id]
            output_owners = utxo.get_output_owners()

            input = transferable_input.input
            address_indices = input.address_indices
            input_signers: List[Address] = len(address_indices) * [ADDRESS_EMPTY]
            for j, address_index in enumerate(address_indices):
                address = output_owners.addresses[address_index.value]
                input_signers[j] = address

            inputs_signers[i] = input_signers

        return inputs_signers
