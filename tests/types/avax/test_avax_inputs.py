from avalanchepy.types.avax.inputs.secp256k1_transfer_input import (
    Secp256k1TransferInput,
)
from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.codecs import AVM_CODEC, PVM_CODEC


def test_secp2561_transfer_input():
    data = bytes([
        # type_id:
        0x00, 0x00, 0x00, 0x05,
        # amount:
        0x00, 0x00, 0x00, 0x00, 0xee, 0x6b, 0x28, 0x00,
        # length:
        0x00, 0x00, 0x00, 0x01,
        # address_indices[0]
        0x00, 0x00, 0x00, 0x00
    ])  # fmt: skip

    (input, leftover) = AVM_CODEC.unpack_prefix(data)
    assert len(leftover) == 0
    assert isinstance(input, Secp256k1TransferInput)
    assert AVM_CODEC.pack_prefix(input) == data


def test_transferable_intput():
    data = bytes([
        # txID:
        0xdf, 0xaf, 0xbd, 0xf5, 0xc8, 0x1f, 0x63, 0x5c,
        0x92, 0x57, 0x82, 0x4f, 0xf2, 0x1c, 0x8e, 0x3e,
        0x6f, 0x7b, 0x63, 0x2a, 0xc3, 0x06, 0xe1, 0x14,
        0x46, 0xee, 0x54, 0x0d, 0x34, 0x71, 0x1a, 0x15,
        # utxoIndex:
        0x00, 0x00, 0x00, 0x01,
        # assetID:
        0x68, 0x70, 0xb7, 0xd6, 0x6a, 0xc3, 0x25, 0x40,
        0x31, 0x13, 0x79, 0xe5, 0xb5, 0xdb, 0xad, 0x28,
        0xec, 0x7e, 0xb8, 0xdd, 0xbf, 0xc8, 0xf4, 0xd6,
        0x72, 0x99, 0xeb, 0xb4, 0x84, 0x75, 0x90, 0x7a,
        # input:
        0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00,
        0xee, 0x6b, 0x28, 0x00, 0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00
    ])  # fmt: skip

    (input, leftover) = TransferableInput.deserialize(data, PVM_CODEC)
    assert len(leftover) == 0
    assert input.serialize(PVM_CODEC) == data


def test_transferable_input_2():
    data = bytes([
        219, 207, 137, 15, 119, 244, 155, 150, 133, 118, 72, 183,
        43, 119, 249, 248, 41, 55, 242, 138, 104, 112, 74, 240,
        93, 160, 220, 18, 186, 83, 242, 219, 0, 0, 0, 5,
        219, 207, 137, 15, 119, 244, 155, 150, 133, 118, 72, 183,
        43, 119, 249, 248, 41, 55, 242, 138, 104, 112, 74, 240,
        93, 160, 220, 18, 186, 83, 242, 219, 0, 0, 0, 5,
        0, 0, 0, 0, 0, 30, 132, 128, 0, 0, 0, 3,
        0, 0, 0, 3, 0, 0, 0, 2, 0, 0, 0, 1
    ])  # fmt: skip

    (input, leftover) = TransferableInput.deserialize(data, PVM_CODEC)
    assert len(leftover) == 0
    assert input.serialize(PVM_CODEC) == data
