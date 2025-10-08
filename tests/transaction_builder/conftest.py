from enum import Enum
from typing import Optional

from avalanchepy.transaction_builder import Context
from avalanchepy.types.avax.inputs.secp256k1_transfer_input import (
    Secp256k1TransferInput,
)
from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.secp256k1_transfer_output import (
    Secp256k1TransferOutput,
)
from avalanchepy.types.avax.outputs.stakeable_lock_out import StakeableLockOut
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.avax.utxoid import UtxoId
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.list_struct import ListStruct
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.seder import Int


class AvaxAssetId(str, Enum):
    MAINNET = ("FvwEAhmxKfeiG8SnEvq42hc6whRyY3EFYAvebMqDNDGCgxN5Z",)
    TESTNET = "U8iRqJoiJm8xZHAacmvYyZVwqQx6uDNtQeP3CQ6fcgQk3JqnK"


TEST_OWNER_X_ADDRESS_STR = "X-fuji1w5jg0xyw2zq22nhpjar834gyeksc6wuleftqzg"
TEST_OWNER_X_ADDRESS = Address.from_string(TEST_OWNER_X_ADDRESS_STR)

TEST_UTXO_ID_1_HEX = "0x009e71412d5b89d0b51e679a93cf59966c3c89346949f1976f930feddbfd765d"
TEST_UTXO_ID_1 = Id(value=bytes.fromhex(TEST_UTXO_ID_1_HEX[2:]))

TEST_UTXO_ID_2_HEX = "0xd1f6526c4233a5af42b0c8311a9824a84f73b3e32ba637aaa7d9dd4994bccbad"
TEST_UTXO_ID_2 = Id(value=bytes.fromhex(TEST_UTXO_ID_2_HEX[2:]))

TEST_AVAX_ASSET_ID = Id.from_string(AvaxAssetId.TESTNET)
TEST_P_BLOCKCHAIN_ID_STR = "11111111111111111111111111111111LpoYY"

TEST_CONTEXT = Context(
    avax_asset_id=TEST_AVAX_ASSET_ID, network_id=Int(value=1), p_blockchain_id=Id.from_string(TEST_P_BLOCKCHAIN_ID_STR)
)


def get_utxo(amount: Long, asset_id: Id = TEST_AVAX_ASSET_ID):
    return Utxo(
        utxo_id=UtxoId(id=TEST_UTXO_ID_1, output_idx=Int(value=0)),
        asset_id=asset_id,
        output=Secp256k1TransferOutput(
            amount=amount,
            output_owners=Secp256k1OutputOwners(
                locktime=Long(value=0),
                threshold=Int(value=1),
                addresses=ListStruct[Address](list=[TEST_OWNER_X_ADDRESS]),
            ),
        ),
    )


def get_transferable_output(
    amount: Long,
    locktime: Optional[Long] = None,
    threshold: Optional[Int] = None,
) -> TransferableOutput:
    if locktime is None:
        locktime = Long(value=0)

    if threshold is None:
        threshold = Int(value=1)

    return TransferableOutput(
        asset_id=TEST_AVAX_ASSET_ID,
        output=Secp256k1TransferOutput(
            amount=amount,
            output_owners=Secp256k1OutputOwners(
                locktime=locktime,
                threshold=threshold,
                addresses=ListStruct[Address](list=[TEST_OWNER_X_ADDRESS]),
            ),
        ),
    )


def get_stakeable_locked_output(amount: Long, locktime: Long) -> TransferableOutput:
    return TransferableOutput(
        asset_id=TEST_AVAX_ASSET_ID,
        output=StakeableLockOut(
            locktime=locktime,
            transferable_output=Secp256k1TransferOutput(
                amount=amount,
                output_owners=Secp256k1OutputOwners(
                    locktime=Long(value=0),
                    threshold=Int(value=1),
                    addresses=ListStruct[Address](list=[TEST_OWNER_X_ADDRESS]),
                ),
            ),
        ),
    )


def get_transferable_input(amount: Optional[Long] = None) -> TransferableInput:
    if amount is None:
        amount = Long(value=50000000000)

    return TransferableInput(
        utxo_id=UtxoId(
            id=TEST_UTXO_ID_1,
            output_idx=Int(value=0),
        ),
        asset_id=TEST_CONTEXT.avax_asset_id,
        input=Secp256k1TransferInput(
            amount=amount,
            address_indices=ListStruct[Int](list=[Int(value=0)]),
        ),
    )
