from avalanchepy.contants import PRIMARY_NETWORK_ID
from avalanchepy.transaction_builder import TransactionBuilder
from avalanchepy.transaction_builder.types import SpendOptions
from avalanchepy.types.avax.add_permissionless_delegator_tx import (
    AddPermissionlessDelegatorTx,
)
from avalanchepy.types.avax.base_tx import BaseTx
from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.avax.outputs.secp256k1_output_owners import Secp256k1OutputOwners
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.avax.subnet_validator import SubnetValidator
from avalanchepy.types.avax.validator import Validator
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.list_struct import ListStruct
from avalanchepy.types.primitives.long import Long
from avalanchepy.types.primitives.node_id import NodeId
from avalanchepy.types.seder import Int
from tests.transaction_builder.conftest import (
    TEST_CONTEXT,
    TEST_OWNER_X_ADDRESS,
    get_transferable_input,
    get_transferable_output,
    get_utxo,
)

TEST_NODE_ID_STR = "NodeID-2m38qc95mhHXtrhjyGbe7r2NhniqHHJRB"


def test_build_add_permissionless_delegator_tx():
    transaction_builder = TransactionBuilder(TEST_CONTEXT)

    amount = Long(value=1800000)
    utxo_amount = Long(value=2 * (10**9))
    spend_options = SpendOptions.default([TEST_OWNER_X_ADDRESS])
    subnet_validator = SubnetValidator(
        validator=Validator(
            node_id=NodeId.from_string(TEST_NODE_ID_STR),
            start_time=Long(value=0),
            end_time=Long(value=120),
            weight=amount,
        ),
        subnet_id=PRIMARY_NETWORK_ID,
    )
    rewards_owner = Secp256k1OutputOwners(
        locktime=Long(value=0), threshold=Int(value=1), addresses=ListStruct[Address].empty()
    )
    actual_tx = transaction_builder.build_add_permissionless_delegator_tx(
        delegator=TEST_OWNER_X_ADDRESS,
        utxos=[get_utxo(utxo_amount)],
        subnet_validator=subnet_validator,
        rewards_owner=rewards_owner,
        options=spend_options,
    )

    add_primary_network_delegator_fee = Long(value=10000)
    expected = AddPermissionlessDelegatorTx(
        base_tx=BaseTx(
            network_id=TEST_CONTEXT.network_id,
            blockchain_id=TEST_CONTEXT.p_blockchain_id,
            outputs=ListStruct[TransferableOutput](
                list=[
                    get_transferable_output(
                        utxo_amount - amount - add_primary_network_delegator_fee,
                    )
                ]
            ),
            inputs=ListStruct[TransferableInput](list=[get_transferable_input(utxo_amount)]),
            memo=spend_options.memo,
        ),
        subnet_validator=subnet_validator,
        stake_outputs=ListStruct[TransferableOutput](list=[get_transferable_output(amount)]),
        delegator_rewards_owner=rewards_owner,
    )

    assert actual_tx == expected
