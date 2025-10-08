from avalanchepy.types.primitives.utils import (
    decode_bech32_to_bytes,
    encode_bech32_to_str,
)

TEST_HRP = "fuji"
TEST_BECH32_DECODED_DATA = bytes(
    [126, 38, 59, 7, 199, 172, 12, 22, 147, 53, 182, 1, 148, 236, 167, 174, 169, 244, 65, 198]
)

TEST_BECH32_ENCODED_STR = "fuji10cnrkp784sxpdye4kcqefm98465lgswx74khcr"


def test_decode_bech32():
    hrp, res = decode_bech32_to_bytes(TEST_BECH32_ENCODED_STR)

    assert hrp == TEST_HRP
    assert res == TEST_BECH32_DECODED_DATA


def test_encode_bech32():
    encoded = encode_bech32_to_str(TEST_HRP, TEST_BECH32_DECODED_DATA)
    assert encoded == TEST_BECH32_ENCODED_STR
