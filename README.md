# AvalanchePy - The Avalanche Platform Python Library

## Overview

AvalanchePy is a Python Library for interfacing with the Avalanche Platform. This library was developed from the Twinstake API project.

Using AvalanchePy, developers can:

- Work with AVAX primitive types
- Build and sign `AddPermissionlessDelegatorTx` transactions
- Perform UTXO spend calculations
- Issue signed transactions
- Utilize the P-chain (Platform Chain) client for interacting with signed transactions

### Requirements

AvalanchePy requires Python 3.11 or higher.

## Installation

To install AvalanchePy, use:

```shell
$ pip install avalanchepy
```

## Usage

The AvalanchePy library can be imported into your existing Python project as follows:

```python
from avalanchepy.clients.p_client import PClient
from avalanchepy.types.avax.signed_tx import SignedTx
from avalanchepy.transaction_builder import TransactionBuilder

# Create a TransactionBuilder based on your context
tx_builder = TransactionBuilder(YOUR_CONTEXT)
transaction = tx_builder.build_add_permissionless_delegator_tx(...)

# Create credentials list
credentials = [...]  # Fill in with actual credentials

# Initialize a PClient with your URL
p_client = PClient(YOUR_URL)

# Create and issue signed transaction
signed_tx = SignedTx(
    unsigned_transaction=transaction,
    credentials=credentials,
)

# Issue the transaction and retrieve the transaction ID
tx_id_str = p_client.issue_tx(signed_tx)
```

Please check out the `tests` folder for more info and examples.

## License

This project is licensed under the MIT License.
