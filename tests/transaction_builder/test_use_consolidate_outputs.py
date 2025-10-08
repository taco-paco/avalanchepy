from avalanchepy.transaction_builder.use_consolidate_output import (
    can_combine,
    combine,
    consolidate,
)
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.primitives.long import Long
from tests.transaction_builder.conftest import (
    TEST_AVAX_ASSET_ID,
    get_stakeable_locked_output,
    get_transferable_output,
)


def test_use_consolidate_outputs():
    a = get_transferable_output(amount=Long(value=100))
    b = get_transferable_output(amount=Long(value=50))
    c = get_transferable_output(amount=Long(value=50))

    result = consolidate([a, b, c], can_combine, combine)
    assert len(result) == 1

    output = result[0]
    assert output.amount() == Long(value=200)
    assert output.asset_id == TEST_AVAX_ASSET_ID
    assert isinstance(output.output, Secp256k1TransferOutput)


def test_consolidate_different_outputs():
    x1 = get_transferable_output(Long(value=50))
    x2 = get_transferable_output(Long(value=100))

    y1 = get_stakeable_locked_output(Long(value=100), Long(value=0))
    y2 = get_stakeable_locked_output(Long(value=200), Long(value=0))

    result = consolidate([x1, x2, y1, y2], can_combine, combine)
    assert len(result) == 2

    output1 = result[0]
    assert isinstance(output1.output, Secp256k1TransferOutput)
    assert output1.amount() == Long(value=150)
    assert output1.asset_id == TEST_AVAX_ASSET_ID

    output2 = result[1]
    assert isinstance(output2.output, StakeableLockOut)
    assert output2.amount() == Long(value=300)
    assert output2.asset_id == TEST_AVAX_ASSET_ID
