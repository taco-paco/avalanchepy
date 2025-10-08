from typing import Annotated, ClassVar, Tuple

from pydantic import AfterValidator, BaseModel

from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.utils import validate_bytes_length
from avalanchepy.types.seder import Codec, Seder

SECP256K1_SIGNATURE_LEN = 65


class Secp256k1Signature(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.Signature

    value: Annotated[bytes, AfterValidator(lambda x: validate_bytes_length(x, SECP256K1_SIGNATURE_LEN))]

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Secp256k1Signature", bytes]:
        if len(data) < SECP256K1_SIGNATURE_LEN:
            raise DeserializationError.invalid_size(len(data), SECP256K1_SIGNATURE_LEN)

        return Secp256k1Signature(value=data[:SECP256K1_SIGNATURE_LEN]), data[SECP256K1_SIGNATURE_LEN:]

    def serialize(self, codec: Codec) -> bytes:
        return self.value
