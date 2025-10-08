from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.avax.validator import Validator
from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.seder import Codec, Seder


class SubnetValidator(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.SubnetValidator

    validator: Validator
    subnet_id: Id

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["SubnetValidator", bytes]:
        (validator, data) = Validator.deserialize(data, codec)
        (subnet_id, data) = Id.deserialize(data, codec)

        return SubnetValidator(subnet_id=subnet_id, validator=validator), data

    def serialize(self, codec: Codec) -> bytes:
        data = self.validator.serialize(codec)
        data += self.subnet_id.serialize(codec)

        return data
