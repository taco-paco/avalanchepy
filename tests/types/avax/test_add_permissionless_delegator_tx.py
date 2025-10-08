from avalanchepy.types.avax.add_permissionless_delegator_tx import (
    AddPermissionlessDelegatorTx,
)
from avalanchepy.types.codecs import DEFAULT_CODEC_VERSION, PVM_CODEC
from avalanchepy.types.utils import pack_codec, unpack_codec
from tests.conftest import TEST_ADD_PERMISSIONALESS_DELEGATOR_TX_RAW


def test_add_permissionless_delegator_tx():
    (tx, leftover) = AddPermissionlessDelegatorTx.deserialize(TEST_ADD_PERMISSIONALESS_DELEGATOR_TX_RAW, PVM_CODEC)
    assert len(leftover) == 0
    assert tx.serialize(PVM_CODEC) == TEST_ADD_PERMISSIONALESS_DELEGATOR_TX_RAW

    data = bytes([0, 0, 0, 0x1A]) + TEST_ADD_PERMISSIONALESS_DELEGATOR_TX_RAW
    (tx, leftover) = PVM_CODEC.unpack_prefix(data)
    assert len(leftover) == 0
    assert PVM_CODEC.pack_prefix(tx) == data

    packed_data = pack_codec(PVM_CODEC, tx)
    assert packed_data == DEFAULT_CODEC_VERSION.serialize(PVM_CODEC) + data

    (tx, leftover) = unpack_codec(AddPermissionlessDelegatorTx, PVM_CODEC, packed_data)
    assert len(leftover) == 0
    assert isinstance(tx, AddPermissionlessDelegatorTx)
