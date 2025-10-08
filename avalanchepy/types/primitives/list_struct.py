from typing import Generic, List, Tuple, Type, TypeVar

from pydantic import BaseModel, model_serializer

from avalanchepy.types.seder import Codec, Int, Serializable


class Combined(Serializable, BaseModel):
    pass


T = TypeVar("T", bound=Combined)


class ListStruct(BaseModel, Generic[T]):
    """
    A generic wrapper around a list that provides serialization and item access via the `[]` operator.

    Attributes:
        list (List[T]): The underlying list of items.
    """

    list: List[T]

    @model_serializer(return_type=List[T])
    def model_serialize(self) -> List[T]:
        return self.list

    def serialize(self, codec: Codec) -> bytes:
        data = Int(value=len(self.list)).serialize(codec)
        for el in self.list:
            data += el.serialize(codec)

        return data

    def pack_list(self, codec: Codec) -> bytes:
        data = Int(value=len(self.list)).serialize(codec)
        for el in self.list:
            data += codec.pack_prefix(el)

        return data

    def append(self, item: T):
        self.list.append(item)

    @staticmethod
    def empty() -> "ListStruct[T]":
        return ListStruct[T](list=[])

    def __getitem__(self, index: int) -> T:
        """
        Access list elements using the `[]` operator.

        Args:
            index (int): The index of the item to retrieve.

        Returns:
            T: The item at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self.list[index]

    def __iter__(self):
        """
        Enable iteration over the ListStruct object.

        Returns:
            iterator: An iterator over the underlying list.
        """
        return iter(self.list)

    def __len__(self) -> int:
        """
        Enable the use of len() on ListStruct objects.

        Returns:
           int: The length of the underlying list.
        """
        return len(self.list)


D = TypeVar("D", bound=Combined)


def deserialize_list(type: Type[D], data: bytes, codec: Codec) -> Tuple["ListStruct[D]", bytes]:
    (length, data) = Int.deserialize(data, codec)

    list: List[D] = []
    for _ in range(length.value):
        (el, data) = type.deserialize(data, codec)
        list.append(el)

    return ListStruct[D].model_construct(list=list), data
