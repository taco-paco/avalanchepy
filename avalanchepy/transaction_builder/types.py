from datetime import datetime, timezone
from typing import Callable, Dict, List, Tuple

from avalanchepy.types.avax.inputs.transferable_input import TransferableInput
from avalanchepy.types.avax.outputs.transferable_output import TransferableOutput
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.primitives.address import Address
from avalanchepy.types.primitives.byte import Byte
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.list_struct import ListStruct


class SpendOptions:
    min_issuance_time: int
    change_addresses: List[Address]
    threshold: int
    memo: ListStruct[Byte]
    locktime: int

    def __init__(
        self,
        min_issuance_time: int,
        change_addresses: List[Address],
        threshold: int,
        memo: ListStruct[Byte],
        locktime: int,
    ):
        self.min_issuance_time = min_issuance_time
        self.change_addresses = change_addresses
        self.threshold = threshold
        self.memo = memo
        self.locktime = locktime

    @staticmethod
    def default(adresses: List[Address]) -> "SpendOptions":
        return SpendOptions(
            min_issuance_time=int(datetime.now(timezone.utc).timestamp()),
            change_addresses=adresses,
            threshold=1,
            memo=ListStruct(list=[]),
            locktime=0,
        )


class UtxoCalculationParams:
    utxos: List[Utxo]
    from_addresses: List[Address]
    options: SpendOptions

    def __init__(self, utxos: List[Utxo], from_addresses: List[Address], options: SpendOptions):
        self.utxos = utxos
        self.from_addresses = from_addresses
        self.options = options


class UtxoCalculationResult:
    inputs: List[TransferableInput]
    stake_outputs: List[TransferableOutput]
    change_outputs: List[TransferableOutput]

    def __init__(
        self,
        inputs: List[TransferableInput],
        stake_outputs: List[TransferableOutput],
        change_outputs: List[TransferableOutput],
    ):
        self.inputs = inputs
        self.stake_outputs = stake_outputs
        self.change_outputs = change_outputs


class UtxoCalculationState:
    amounts_to_burn: Dict[Id, int]
    amounts_to_stake: Dict[Id, int]

    def __init__(self, amounts_to_burn: Dict[Id, int], amounts_to_stake: Dict[Id, int]):
        self.amounts_to_burn = amounts_to_burn
        self.amounts_to_stake = amounts_to_stake

    # returns excess
    def consume_locked_asset(self, asset_id: Id, amount: int) -> int:
        to_stake = min(self.amounts_to_stake.get(asset_id, 0), amount)
        self.amounts_to_stake[asset_id] = self.amounts_to_stake.get(asset_id, 0) - to_stake

        return amount - to_stake


UtxoCalculationFn = Callable[
    [UtxoCalculationParams, UtxoCalculationState, UtxoCalculationResult],
    Tuple[UtxoCalculationState, UtxoCalculationResult],
]
