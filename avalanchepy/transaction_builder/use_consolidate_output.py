from typing import Callable, List, Tuple, TypeVar

from avalanchepy.transaction_builder.types import (
    UtxoCalculationParams,
    UtxoCalculationResult,
    UtxoCalculationState,
)
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput


def can_combine(a: TransferableOutput, b: TransferableOutput) -> bool:
    if a.asset_id != b.asset_id:
        return False

    if isinstance(a.output, StakeableLockOut) and isinstance(b.output, StakeableLockOut):
        return a.output.locktime == b.output.locktime and a.output_owners() == b.output_owners()

    if isinstance(a.output, Secp256k1TransferOutput) and isinstance(b.output, Secp256k1TransferOutput):
        return a.output_owners() == b.output_owners()

    return False


def combine(a: TransferableOutput, b: TransferableOutput) -> TransferableOutput:
    if isinstance(a.output, StakeableLockOut) and isinstance(b.output, StakeableLockOut):
        return TransferableOutput(
            asset_id=a.asset_id,
            output=StakeableLockOut(
                locktime=a.output.locktime,
                transferable_output=Secp256k1TransferOutput(
                    amount=a.amount() + b.amount(),
                    output_owners=a.output_owners(),
                ),
            ),
        )

    if isinstance(a.output, Secp256k1TransferOutput) and isinstance(b.output, Secp256k1TransferOutput):
        return TransferableOutput(
            asset_id=a.asset_id,
            output=Secp256k1TransferOutput(
                amount=a.output.amount + b.output.amount,
                output_owners=a.output.output_owners,
            ),
        )

    raise ValueError("Calling combine on incompatible TransferableOutputs")


T = TypeVar("T")
CanCombineFn = Callable[[T, T], bool]
CombineFn = Callable[[T, T], T]


def consolidate(arr: List[T], can_combine_fn: CanCombineFn, combine_fn: CombineFn) -> List[T]:
    """
    Consolidates a list of elements by combining them based on the provided functions.

    Args:
        arr (List[T]): The list of elements to consolidate.
        can_combine_fn (CanCombineFn): A function that determines if two elements can be combined.
        combine_fn (CombineFn): A function that combines two elements into one.

    Returns:
        List[T]: The consolidated list of elements.
    """
    consolidated: List[T] = []
    for el in arr:
        combined = False
        for i, existing in enumerate(consolidated):
            if can_combine_fn(existing, el):
                consolidated[i] = combine_fn(existing, el)
                combined = True
                break
        if not combined:
            consolidated.append(el)

    return consolidated


def use_consolidate_output(
    _: UtxoCalculationParams, state: UtxoCalculationState, current_results: UtxoCalculationResult
) -> Tuple[UtxoCalculationState, UtxoCalculationResult]:
    consolidated_change_outputs = consolidate(current_results.change_outputs, can_combine, combine)
    consolidated_stake_outputs = consolidate(current_results.stake_outputs, can_combine, combine)

    return state, UtxoCalculationResult(
        inputs=current_results.inputs,
        stake_outputs=consolidated_stake_outputs,
        change_outputs=consolidated_change_outputs,
    )
