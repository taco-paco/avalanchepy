from typing import Tuple, Type, TypeVar

from avalanchepy.types.codecs import DEFAULT_CODEC_VERSION
from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.short import Short
from avalanchepy.types.seder import Codec, Seder, Serializable

S = TypeVar("S", bound=Serializable)


def pack_codec(codec: Codec, ser: S) -> bytes:
    return DEFAULT_CODEC_VERSION.serialize(codec) + codec.pack_prefix(ser)


def pack_codec_direct(codec: Codec, ser: S) -> bytes:
    return DEFAULT_CODEC_VERSION.serialize(codec) + ser.serialize(codec)


D = TypeVar("D", bound=Seder)


def unpack_codec(der: Type[D], codec: Codec, data: bytes) -> Tuple[D, bytes]:
    codec_version, data = Short.deserialize(data, codec)
    if codec_version.value != DEFAULT_CODEC_VERSION.value:
        raise DeserializationError("Unsupported codec version: {codec_version}")

    deserialized, data = codec.unpack_prefix(data)
    if not isinstance(deserialized, der):
        raise DeserializationError(f"Unexpected type: expected {der._type}, got {deserialized._type}")

    return deserialized, data


def unpack_codec_direct(der: Type[D], codec: Codec, data: bytes) -> Tuple[D, bytes]:
    codec_version, data = Short.deserialize(data, codec)
    if codec_version.value != DEFAULT_CODEC_VERSION.value:
        raise DeserializationError("Unsupported codec version: {codec_version}")

    deserialized, data = der.deserialize(data, codec)
    return deserialized, data
