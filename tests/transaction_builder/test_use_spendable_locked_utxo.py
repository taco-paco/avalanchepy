# Based on https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/vms/pvm/utxoCalculationFns/useSpendableLockedUTXOs.test.ts # noqa: E501

from datetime import datetime, timezone
from typing import Optional

from avalanchepy.transaction_builder.types import (
    SpendOptions,
    UtxoCalculationParams,
    UtxoCalculationResult,
    UtxoCalculationState,
)
from avalanchepy.transaction_builder.use_spendable_locked_utxo import (
    use_spendable_locked_utxo,
)
from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.avax.utxoid import UtxoId
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.list_struct import ListStruct
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Int
from tests.transaction_builder.conftest import (
    TEST_AVAX_ASSET_ID,
    TEST_OWNER_X_ADDRESS,
    TEST_UTXO_ID_1,
    TEST_UTXO_ID_2,
)


def get_stakeable_locked_utxo(
    id: Id,
    amount: Long,
    locktime: Optional[Long] = None,
    asset_id: Id = TEST_AVAX_ASSET_ID,
) -> Utxo:
    if locktime is None:
        locktime = Long(value=int(datetime.now(timezone.utc).timestamp()))

    return Utxo(
        utxo_id=UtxoId(id=id, output_idx=Int(value=0)),
        asset_id=asset_id,
        output=StakeableLockOut(
            locktime=locktime,
            transferable_output=Secp256k1TransferOutput(
                amount=amount,
                output_owners=Secp256k1OutputOwners(
                    locktime=Long(value=0),
                    threshold=Int(value=1),
                    addresses=ListStruct[Address](list=[TEST_OWNER_X_ADDRESS]),
                ),
            ),
        ),
    )


def test_not_locked_anymore():
    stakeable_utxo_amount1 = Long(value=600000000)
    stakeable_utxo_amount2 = Long(value=700000000)
    amount_remaining_to_stake = 500000000
    locktime = Long(value=1)

    utxo1 = get_stakeable_locked_utxo(TEST_UTXO_ID_1, stakeable_utxo_amount1, locktime=locktime)
    utxo2 = get_stakeable_locked_utxo(TEST_UTXO_ID_2, stakeable_utxo_amount2, locktime=locktime)

    params = UtxoCalculationParams(
        utxos=[utxo1, utxo2],
        from_addresses=[TEST_OWNER_X_ADDRESS],
        options=SpendOptions(
            min_issuance_time=2 * locktime.value,
            change_addresses=[TEST_OWNER_X_ADDRESS],
            threshold=1,
            memo=ListStruct(list=[]),
            locktime=0,
        ),
    )
    state = UtxoCalculationState(
        amounts_to_burn={},
        amounts_to_stake={
            TEST_AVAX_ASSET_ID: amount_remaining_to_stake,
        },
    )
    result = UtxoCalculationResult([], [], [])
    state, result = use_spendable_locked_utxo(params, state, result)

    assert len(result.change_outputs) == 0
    assert len(result.inputs) == 0
    assert state.amounts_to_stake.get(TEST_AVAX_ASSET_ID) == amount_remaining_to_stake


def test_stake_not_covered():
    stakeable_utxo_amount1 = Long(value=200000000)
    stakeable_utxo_amount2 = Long(value=100000000)
    amount_remaining_to_stake = 500000000

    utxo1 = get_stakeable_locked_utxo(TEST_UTXO_ID_1, stakeable_utxo_amount1)
    utxo2 = get_stakeable_locked_utxo(TEST_UTXO_ID_2, stakeable_utxo_amount2)

    params = UtxoCalculationParams(
        utxos=[utxo1, utxo2],
        from_addresses=[TEST_OWNER_X_ADDRESS],
        options=SpendOptions(
            min_issuance_time=0,
            change_addresses=[TEST_OWNER_X_ADDRESS],
            threshold=1,
            memo=ListStruct(list=[]),
            locktime=0,
        ),
    )
    state = UtxoCalculationState(
        amounts_to_burn={},
        amounts_to_stake={
            TEST_AVAX_ASSET_ID: amount_remaining_to_stake,
        },
    )
    result = UtxoCalculationResult([], [], [])
    state, result = use_spendable_locked_utxo(params, state, result)

    assert len(result.change_outputs) == 0
    assert (
        state.amounts_to_stake.get(TEST_AVAX_ASSET_ID)
        == amount_remaining_to_stake - stakeable_utxo_amount2.value - stakeable_utxo_amount1.value
    )


def test_stake_covered():
    stakeable_utxo_amount1 = Long(value=200000000)
    stakeable_utxo_amount2 = Long(value=400000000)
    amount_remaining_to_stake = 500000000

    utxo1 = get_stakeable_locked_utxo(TEST_UTXO_ID_1, stakeable_utxo_amount1)
    utxo2 = get_stakeable_locked_utxo(TEST_UTXO_ID_2, stakeable_utxo_amount2)

    params = UtxoCalculationParams(
        utxos=[utxo1, utxo2],
        from_addresses=[TEST_OWNER_X_ADDRESS],
        options=SpendOptions(
            min_issuance_time=0,
            change_addresses=[TEST_OWNER_X_ADDRESS],
            threshold=1,
            memo=ListStruct(list=[]),
            locktime=0,
        ),
    )
    state = UtxoCalculationState(
        amounts_to_burn={},
        amounts_to_stake={
            TEST_AVAX_ASSET_ID: amount_remaining_to_stake,
        },
    )
    result = UtxoCalculationResult([], [], [])
    state, result = use_spendable_locked_utxo(params, state, result)

    assert len(result.change_outputs) == 1
    assert (
        result.change_outputs[0].amount().value
        == stakeable_utxo_amount1.value + stakeable_utxo_amount2.value - amount_remaining_to_stake
    )
    assert state.amounts_to_stake.get(TEST_AVAX_ASSET_ID) == 0

    assert len(result.inputs) == 2
    assert result.inputs[0].utxo_id.id == TEST_UTXO_ID_1
    assert result.inputs[0].amount() == stakeable_utxo_amount1
    assert result.inputs[1].utxo_id.id == TEST_UTXO_ID_2
    assert result.inputs[1].amount() == stakeable_utxo_amount2


def test_mixed_asset_ids():
    stakeable_utxo_amount1 = Long(value=200000000)
    stakeable_utxo_amount2 = Long(value=400000000)
    amount_remaining_to_stake = 500000000

    utxo1 = get_stakeable_locked_utxo(TEST_UTXO_ID_1, stakeable_utxo_amount1)
    utxo2 = get_stakeable_locked_utxo(TEST_UTXO_ID_2, stakeable_utxo_amount2, asset_id=Id(value=bytes(32 * [1])))

    params = UtxoCalculationParams(
        utxos=[utxo1, utxo2],
        from_addresses=[TEST_OWNER_X_ADDRESS],
        options=SpendOptions(
            min_issuance_time=0,
            change_addresses=[TEST_OWNER_X_ADDRESS],
            threshold=1,
            memo=ListStruct(list=[]),
            locktime=0,
        ),
    )
    state = UtxoCalculationState(
        amounts_to_burn={},
        amounts_to_stake={
            TEST_AVAX_ASSET_ID: amount_remaining_to_stake,
        },
    )
    result = UtxoCalculationResult([], [], [])
    state, result = use_spendable_locked_utxo(params, state, result)

    assert len(result.change_outputs) == 0
    assert state.amounts_to_stake.get(TEST_AVAX_ASSET_ID) == amount_remaining_to_stake - stakeable_utxo_amount1.value
