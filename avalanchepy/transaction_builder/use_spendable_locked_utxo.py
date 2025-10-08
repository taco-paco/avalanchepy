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
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.primitives.list_struct import ListStruct
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Int


# Based on https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/vms/pvm/utxoCalculationFns/useSpendableLockedUTXOs.ts#L35 # noqa: E501
def use_spendable_locked_utxo(
    params: UtxoCalculationParams, state: UtxoCalculationState, current_results: UtxoCalculationResult
) -> Tuple[UtxoCalculationState, UtxoCalculationResult]:
    class UsableUtxo:
        utxo: Utxo
        locked_output: StakeableLockOut

        def __init__(self, utxo: Utxo, locked_output: StakeableLockOut):
            self.utxo = utxo
            self.locked_output = locked_output

    def filter_map_utxos(utxo: Utxo) -> Optional[UsableUtxo]:
        stakeable_output = try_cast_output_type(utxo.output, StakeableLockOut)
        if stakeable_output is None:
            return None
        if params.options.min_issuance_time >= stakeable_output.locktime.value:
            return None
        if utxo.asset_id not in state.amounts_to_stake or state.amounts_to_stake[utxo.asset_id] == 0:
            return None

        return UsableUtxo(utxo=utxo, locked_output=stakeable_output)

    stakeable_utxos = [utxo for utxo in map(filter_map_utxos, params.utxos) if utxo is not None]
    for stakeable_utxo in stakeable_utxos:
        stakeable_output = stakeable_utxo.locked_output
        transferable_output = stakeable_output.transferable_output

        # skip if necessary amount has been staked
        asset_id = stakeable_utxo.utxo.asset_id
        if state.amounts_to_stake[asset_id] == 0:
            continue

        sigs = transferable_output.match_owners(params.from_addresses, params.options.min_issuance_time)
        if sigs is None:
            continue

        # as an input we get an amount
        current_results.inputs.append(
            TransferableInput(
                utxo_id=stakeable_utxo.utxo.utxo_id,
                asset_id=asset_id,
                input=Secp256k1TransferInput(
                    amount=transferable_output.amount,
                    address_indices=ListStruct[Int](list=[Int(value=sig) for sig in sigs]),
                ),
            )
        )

        # excess is basically a change that we return
        excess = state.consume_locked_asset(stakeable_utxo.utxo.asset_id, transferable_output.amount.value)
        current_results.stake_outputs.append(
            TransferableOutput(
                asset_id=asset_id,
                output=StakeableLockOut(
                    locktime=stakeable_output.locktime,
                    transferable_output=Secp256k1TransferOutput(
                        amount=transferable_output.amount - Long(value=excess),
                        output_owners=transferable_output.output_owners,
                    ),
                ),
            )
        )

        # if change is 0, no need in create ChangeOutput
        if excess == 0:
            continue

        # returns change if amount was larger than toStake. (excess)
        current_results.change_outputs.append(
            TransferableOutput(
                asset_id=asset_id,
                output=StakeableLockOut(
                    locktime=stakeable_output.locktime,
                    transferable_output=Secp256k1TransferOutput(
                        amount=Long(value=excess),
                        output_owners=transferable_output.output_owners,
                    ),
                ),
            )
        )

    return (state, current_results)
