# Based on https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/vms/pvm/utxoCalculationFns/useUnlockedUTXOs.test.ts # noqa: E501

from avalanchepy.transaction_builder.types import (
    SpendOptions,
    UtxoCalculationParams,
    UtxoCalculationResult,
    UtxoCalculationState,
)
from avalanchepy.transaction_builder.use_unlocked_utxo import use_unlocked_utxo
from avalanchepy.types.primitives.long import Long
from tests.transaction_builder.conftest import (
    TEST_AVAX_ASSET_ID,
    TEST_OWNER_X_ADDRESS,
    get_utxo,
)


def test_gas_stake_change():
    params = UtxoCalculationParams(
        utxos=[get_utxo(Long(value=10000))],
        from_addresses=[TEST_OWNER_X_ADDRESS],
        options=SpendOptions.default([TEST_OWNER_X_ADDRESS]),
    )
    state = UtxoCalculationState(
        amounts_to_burn={
            TEST_AVAX_ASSET_ID: 4900,
        },
        amounts_to_stake={
            TEST_AVAX_ASSET_ID: 4900,
        },
    )
    result = UtxoCalculationResult([], [], [])

    state, result = use_unlocked_utxo(params, state, result)
    assert len(result.change_outputs) == 1
    assert result.change_outputs[0].amount().value == 200

    assert len(result.stake_outputs) == 1
    assert result.stake_outputs[0].amount().value == 4900

    assert state.amounts_to_burn[TEST_AVAX_ASSET_ID] == 0
