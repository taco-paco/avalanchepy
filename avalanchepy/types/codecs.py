from avalanchepy.types.avax.add_permissionless_delegator_tx import (
    AddPermissionlessDelegatorTx,
)
from avalanchepy.types.avax.base_tx import BaseTx
from avalanchepy.types.avax.credential import Credential
from avalanchepy.types.avax.inputs.secp256k1_transfer_input import (
    Secp256k1TransferInput,
)
from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.primitives.short import Short
from avalanchepy.types.seder import Codec

# based on https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/serializable/pvm/codec.ts#L30 # noqa: E501
# now contains only relevant types
PVM_CODEC = Codec(
    5 * [None]  # 0-4
    + [Secp256k1TransferInput]  # 5
    + [None]  # 6
    + [Secp256k1TransferOutput]  # 7
    + [None]  # 8
    + [Credential]  # 9
    + [None]  # 10
    + [Secp256k1OutputOwners]  # 11
    + 10 * [None]  # 12 - 21
    + [StakeableLockOut]  # 22
    + 3 * [None]  # 23 - 25
    + [AddPermissionlessDelegatorTx]  # 26
    + 7 * [None]  # 27 - 33
    + [BaseTx]  # 34
)

# https://github.com/ava-labs/avalanchejs/blob/06c8738c726ea774b26b54ce8dbdc6588fe137f6/src/serializable/avm/codec.ts#L19
AVM_CODEC = Codec(
    [BaseTx]
    + 4 * [None]  # 1-4
    + [Secp256k1TransferInput]  # 5
    + [None]  # 6
    + [Secp256k1TransferOutput]  # 7
    + 3 * [None]  # 8-10
    + [Secp256k1OutputOwners]  # 11
)

DEFAULT_CODEC_VERSION = Short(value=0)
