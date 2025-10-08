import pytest

from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.id import ID_LEN, Id
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Codec, Int

codec = Codec([None, None])


def test_int():
    int_value = Int(value=13)
    int_bytes = bytes([0x00, 0x00, 0x00, 0x0D])
    assert int_bytes == int_value.serialize(codec)

    (actual, leftover) = Int.deserialize(int_bytes, codec)
    assert len(leftover) == 0
    assert actual == int_value


def test_int_leftover():
    long_value = Int(value=257)
    expected_leftover = bytes([0x02, 0xFF])
    long_bytes = bytes([0x00, 0x00, 0x01, 0x01]) + expected_leftover

    (actual, leftover) = Int.deserialize(long_bytes, codec)
    assert leftover == expected_leftover
    assert actual == long_value


def test_int_insufficient():
    int_bytes = bytes([0, 0, 1])
    with pytest.raises(DeserializationError, match="DeserializationError: Invalid data size. expected 4, actual: 3"):
        (actual, leftover) = Int.deserialize(int_bytes, codec)


def test_long():
    long_value = Long(value=257)
    long_bytes = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01])
    assert long_bytes == long_value.serialize(codec)

    (actual, leftover) = Long.deserialize(long_bytes, codec)
    assert len(leftover) == 0
    assert actual == long_value


def test_long_leftover():
    long_value = Long(value=258)
    expected_leftover = bytes([0x02, 0xFF])
    long_bytes = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02]) + expected_leftover

    (actual, leftover) = Long.deserialize(long_bytes, codec)
    assert leftover == expected_leftover
    assert actual == long_value


def test_address():
    address_bytes = bytes(range(20))
    address_value = Address(value=address_bytes)

    (actual, leftover) = Address.deserialize(address_bytes, codec)
    assert len(leftover) == 0
    assert actual == address_value

    assert address_bytes == address_value.serialize(codec)


def test_address_insufficient():
    address_bytes = bytes(range(18))
    with pytest.raises(DeserializationError, match="DeserializationError: Invalid data size. expected 20, actual: 18"):
        (_, _) = Address.deserialize(address_bytes, codec)


def test_id():
    id_bytes = bytes(range(ID_LEN))
    id_value = Id(value=id_bytes)

    (actual, leftover) = Id.deserialize(id_bytes, codec)
    assert len(leftover) == 0
    assert actual == id_value

    assert id_bytes == actual.serialize(codec)


def test_id_insufficient():
    id_bytes = bytes(range(ID_LEN - 2))
    with pytest.raises(DeserializationError, match="DeserializationError: Invalid data size. expected 32, actual: 30"):
        (_, _) = Id.deserialize(id_bytes, codec)
