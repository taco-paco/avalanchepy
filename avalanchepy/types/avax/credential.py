from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.avax.inputs.secp256k1_signature import Secp256k1Signature
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.list_struct import ListStruct, deserialize_list
from avalanchepy.types.seder import Codec, Seder


class Credential(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.Credential
    signatures: ListStruct[Secp256k1Signature]

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Credential", bytes]:
        signatures, data = deserialize_list(Secp256k1Signature, data, codec)
        return Credential(signatures=signatures), data

    def serialize(self, codec: Codec) -> bytes:
        return self.signatures.serialize(codec)

    @staticmethod
    def empty() -> "Credential":
        return Credential(signatures=ListStruct[Secp256k1Signature].empty())

    def append_signature(self, signature: Secp256k1Signature):
        self.signatures.append(signature)
