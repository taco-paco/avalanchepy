from typing import Optional, Type, TypeVar, Union

from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut

T = TypeVar("T")


def try_cast_output_type(
    value: Union[Secp256k1OutputOwners, Secp256k1TransferOutput, StakeableLockOut], sample: Type[T]
) -> Optional[T]:
    return value if isinstance(value, sample) else None
