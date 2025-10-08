from typing import ClassVar, Tuple

from pydantic import BaseModel

from avalanchepy.types.primitives.constants import TypeSymbols
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.primitives.node_id import NodeId
from avalanchepy.types.seder import Codec, Seder


class Validator(BaseModel, Seder):
    _type: ClassVar[TypeSymbols] = TypeSymbols.Validator

    node_id: NodeId
    start_time: Long
    end_time: Long
    weight: Long

    @staticmethod
    def deserialize(data: bytes, codec: Codec) -> Tuple["Validator", bytes]:
        (node_id, data) = NodeId.deserialize(data, codec)
        (start_time, data) = Long.deserialize(data, codec)
        (end_time, data) = Long.deserialize(data, codec)
        (weight, data) = Long.deserialize(data, codec)

        return Validator(node_id=node_id, start_time=start_time, end_time=end_time, weight=weight), data

    def serialize(self, codec: Codec) -> bytes:
        data = self.node_id.serialize(codec)
        data += self.start_time.serialize(codec)
        data += self.end_time.serialize(codec)
        data += self.weight.serialize(codec)

        return data
