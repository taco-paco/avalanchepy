import hashlib
from typing import Tuple

import base58
import bech32


def pad_left(data: bytes, length: int) -> bytes:
    offset = length - len(data)
    if offset <= 0:
        return data

    return bytes(offset * [0]) + data


def decode_bech32_to_bytes(data: str) -> Tuple[str, bytes]:
    hrp, words = bech32.bech32_decode(data)
    bits = bech32.convertbits(words, 5, 8, False)

    return hrp, bytes(bits)


def encode_bech32_to_str(hrp: str, bits: bytes) -> str:
    words = bech32.convertbits(bits, 8, 5, False)
    return bech32.bech32_encode(hrp, words)


def validate_bytes_length(value: bytes, expected_length: int) -> bytes:
    if len(value) != expected_length:
        raise ValueError(f"Invalid data size. expected {expected_length}, actual: {len(value)}")

    return value


class Base58Check:
    @staticmethod
    def encode(data: bytes) -> str:
        checksum = hashlib.sha256(data).digest()[-4:]
        return base58.b58encode(data + checksum).decode()

    @staticmethod
    def decode(string: str) -> bytes:
        # skipping verification
        decoded = base58.b58decode(string)
        return decoded[:-4]
