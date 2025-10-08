import hashlib
from typing import ClassVar, Tuple

from avalanchepy.types.avax.credential import Credential
from avalanchepy.types.codecs import PVM_CODEC
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.list_struct import ListStruct, deserialize_list
from avalanchepy.types.seder import Codec, Seder


class SignedTx(Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.AvmSignedTx

    unsigned_transaction: Seder
    credentials: ListStruct[Credential]

    def __init__(self, unsigned_transaction: Seder, credentials: ListStruct[Credential]):
        self.unsigned_transaction = unsigned_transaction
        self.credentials = credentials

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["SignedTx", bytes]:
        unsigned_transaction, data = codec.unpack_prefix(data)
        credentials, data = deserialize_list(Codec, data, codec)
        for credential in credentials:
            assert isinstance(credential, Credential), f"Expected Credential, got {type(credential)}"

        return SignedTx(unsigned_transaction=unsigned_transaction, credentials=credentials), data

    def serialize(self, codec: Codec) -> bytes:
        data = codec.pack_prefix(self.unsigned_transaction)
        data += self.credentials.pack_list(codec)

        return data

    def id(self) -> Id:
        data = self.serialize(PVM_CODEC)
        return Id(value=hashlib.sha256(data).digest())
