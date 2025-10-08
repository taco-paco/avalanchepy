from typing import Optional, Tuple

from avalanchepy.transaction_builder.types import (
    UtxoCalculationParams,
    UtxoCalculationResult,
    UtxoCalculationState,
)
from avalanchepy.transaction_builder.utils import try_cast_output_type
from avalanchepy.types.avax.inputs.secp256k1_transfer_input import (
    Secp256k1TransferInput,
)
from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.list_struct import ListStruct
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Int


# Based on https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/vms/pvm/utxoCalculationFns/useUnlockedUTXOs.ts#L19 # noqa: E501
def use_unlocked_utxo(
    params: UtxoCalculationParams, state: UtxoCalculationState, current_result: UtxoCalculationResult
) -> Tuple[UtxoCalculationState, UtxoCalculationResult]:
    class UsableUtxo:
        utxo: Utxo
        transferable_output: Secp256k1TransferOutput

        def __init__(self, utxo: Utxo, transferable_output: Secp256k1TransferOutput):
            self.utxo = utxo
            self.transferable_output = transferable_output

    def filter_map_utxos(utxo: Utxo) -> Optional[UsableUtxo]:
        transferable_output = try_cast_output_type(utxo.output, Secp256k1TransferOutput)
        if transferable_output is not None:
            return UsableUtxo(utxo, transferable_output)

        output = try_cast_output_type(utxo.output, StakeableLockOut)
        if output is None:
            return None

        if params.options.minIssuanceTime < output.locktime.value:
            return None

        transferable_output = output.transferable_output
        return UsableUtxo(utxo, transferable_output)

    change_owners = Secp256k1OutputOwners(
        locktime=Long(value=0), threshold=Int(value=1), addresses=ListStruct[Address](list=[params.from_addresses[0]])
    )

    usable_utxos = [utxo for utxo in map(filter_map_utxos, params.utxos) if utxo is not None]
    for usable_utxo in usable_utxos:
        utxo = usable_utxo.utxo
        transferable_output = usable_utxo.transferable_output
        asset_id = utxo.asset_id

        remaining_amount_to_burn = state.amounts_to_burn.get(asset_id, 0)
        remaining_amount_to_stake = state.amounts_to_stake.get(asset_id, 0)
        if remaining_amount_to_stake == 0 and remaining_amount_to_burn == 0:
            continue

        sigs = transferable_output.match_owners(params.from_addresses, params.options.min_issuance_time)
        if sigs is None:
            continue

        # as an input we get an amount
        amount = transferable_output.amount
        current_result.inputs.append(
            TransferableInput(
                utxo_id=utxo.utxo_id,
                asset_id=asset_id,
                input=Secp256k1TransferInput(
                    amount=amount,
                    address_indices=ListStruct[Int](list=[Int(value=sig) for sig in sigs]),
                ),
            )
        )

        amount_to_burn = min(transferable_output.amount.value, remaining_amount_to_burn)
        state.amounts_to_burn[asset_id] = remaining_amount_to_burn - amount_to_burn

        available_amount_to_stake = amount.value - amount_to_burn
        excess = state.consume_locked_asset(asset_id, available_amount_to_stake)

        # payment - change = price = amount_ta_stake
        amount_to_stake = Long(value=available_amount_to_stake) - Long(value=excess)
        if amount_to_stake.value > 0:
            current_result.stake_outputs.append(
                TransferableOutput(
                    asset_id=asset_id,
                    output=Secp256k1TransferOutput(
                        amount=amount_to_stake,
                        output_owners=change_owners,
                    ),
                )
            )

        if excess > 0:
            current_result.change_outputs.append(
                TransferableOutput(
                    asset_id=asset_id,
                    output=Secp256k1TransferOutput(
                        amount=Long(value=excess),
                        output_owners=change_owners,
                    ),
                )
            )

    return state, current_result
