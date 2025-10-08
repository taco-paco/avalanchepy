from functools import cmp_to_key, reduce
from typing import Dict, List, Tuple

from avalanchepy.transaction_builder.errors import FailedAction, InsufficientFundsError
from avalanchepy.transaction_builder.types import (
    SpendOptions,
    UtxoCalculationFn,
    UtxoCalculationParams,
    UtxoCalculationResult,
    UtxoCalculationState,
)
from avalanchepy.transaction_builder.use_consolidate_output import (
    use_consolidate_output,
)
from avalanchepy.transaction_builder.use_spendable_locked_utxo import (
    use_spendable_locked_utxo,
)
from avalanchepy.transaction_builder.use_unlocked_utxo import use_unlocked_utxo
from avalanchepy.types.avax.add_permissionless_delegator_tx import (
    AddPermissionlessDelegatorTx,
)
from avalanchepy.types.avax.base_tx import BaseTx
from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.avax.subnet_validator import SubnetValidator
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.codecs import AVM_CODEC, PVM_CODEC
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.list_struct import ListStruct
from avalanchepy.types.seder import Int


class Context:
    avax_asset_id: Id
    network_id: Int
    p_blockchain_id: Id

    def __init__(self, avax_asset_id: Id, network_id: Int, p_blockchain_id: Id):
        self.avax_asset_id = avax_asset_id
        self.network_id = network_id
        self.p_blockchain_id = p_blockchain_id


def compare_transferable_outputs(output1: TransferableOutput, output2: TransferableOutput) -> int:
    if output1.asset_id < output2.asset_id:
        return -1
    if output1.asset_id > output2.asset_id:
        return 1

    pvm_output_types = StakeableLockOut  # Tuple for type checking

    codec1 = PVM_CODEC if isinstance(output1.output, pvm_output_types) else AVM_CODEC
    codec2 = PVM_CODEC if isinstance(output2.output, pvm_output_types) else AVM_CODEC

    # Use native comparison of serialized bytes
    serialized_output1 = output1.serialize(codec1)
    serialized_output2 = output2.serialize(codec2)

    if serialized_output1 < serialized_output2:
        return -1
    if serialized_output1 > serialized_output2:
        return 1

    return 0


class TransactionBuilder:
    context: Context

    def __init__(self, context: Context):
        self.context = context

    # https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/vms/utils/calculateSpend/calculateSpend.ts#L56
    # https://github.com/ava-labs/avalanchego/blob/51d2ee6a55ac9c910198a0c9a8568ef26af67baa/wallet/chain/p/builder/builder.go#L1562
    @staticmethod
    def spend(
        utxos: List[Utxo],
        from_addresses: List[Address],
        amounts_to_burn: Dict[Id, int],
        amounts_to_stake: Dict[Id, int],
        options: SpendOptions,
    ) -> UtxoCalculationResult:
        # read-only state
        params = UtxoCalculationParams(utxos=utxos, from_addresses=from_addresses, options=options)
        # evolving state
        state = UtxoCalculationState(
            amounts_to_burn=amounts_to_burn,
            amounts_to_stake=amounts_to_stake,
        )
        # accumulated results
        result = UtxoCalculationResult([], [], [])

        def verify(
            _: UtxoCalculationParams, state: UtxoCalculationState, current_results: UtxoCalculationResult
        ) -> Tuple[UtxoCalculationState, UtxoCalculationResult]:
            for asset_id, amount in state.amounts_to_burn.items():
                if amount != 0:
                    raise InsufficientFundsError(FailedAction.Burn, asset_id, amount)

            for asset_id, amount in state.amounts_to_stake.items():
                if amount != 0:
                    raise InsufficientFundsError(FailedAction.Stake, asset_id, amount)

            return state, current_results

        def post_processing(
            _: UtxoCalculationParams, state: UtxoCalculationState, current_results: UtxoCalculationResult
        ) -> Tuple[UtxoCalculationState, UtxoCalculationResult]:
            current_results.inputs.sort(key=lambda tx_input: tx_input.utxo_id)
            current_results.stake_outputs.sort(key=cmp_to_key(compare_transferable_outputs))
            current_results.change_outputs.sort(key=cmp_to_key(compare_transferable_outputs))
            return state, current_results

        # calculators
        calculators = [use_spendable_locked_utxo, use_unlocked_utxo, use_consolidate_output, verify, post_processing]

        def reducer(
            acc_combined_state: Tuple[UtxoCalculationState, UtxoCalculationResult], f: UtxoCalculationFn
        ) -> Tuple[UtxoCalculationState, UtxoCalculationResult]:
            acc_state, acc_result = acc_combined_state
            return f(params, acc_state, acc_result)

        (_, result) = reduce(reducer, calculators, (state, result))
        return result

    # https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/vms/pvm/builder.ts#L586
    # https://github.com/ava-labs/avalanchego/blob/51d2ee6a55ac9c910198a0c9a8568ef26af67baa/wallet/chain/p/builder/builder.go#L1365
    def build_add_permissionless_delegator_tx(
        self,
        delegator: Address,
        utxos: List[Utxo],
        subnet_validator: SubnetValidator,
        rewards_owner: Secp256k1OutputOwners,
        options: SpendOptions,
    ) -> AddPermissionlessDelegatorTx:
        # TODO: constant?
        to_burn = {
            self.context.avax_asset_id: 10000,
        }
        to_stake = {self.context.avax_asset_id: subnet_validator.validator.weight.value}

        result = TransactionBuilder.spend(utxos, [delegator], to_burn, to_stake, options)
        return AddPermissionlessDelegatorTx(
            base_tx=BaseTx(
                network_id=self.context.network_id,
                blockchain_id=self.context.p_blockchain_id,
                outputs=ListStruct[TransferableOutput](list=result.change_outputs),
                inputs=ListStruct[TransferableInput](list=result.inputs),
                memo=options.memo,
            ),
            subnet_validator=subnet_validator,
            stake_outputs=ListStruct[TransferableOutput](list=result.stake_outputs),
            delegator_rewards_owner=rewards_owner,
        )
