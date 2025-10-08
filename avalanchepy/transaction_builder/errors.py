from enum import Enum

from avalanchepy.types.primitives.id import Id


class FailedAction(str, Enum):
    Stake = "Stake"
    Burn = "Burn"


class InsufficientFundsError(Exception):
    """A custom exception to represent insufficient fund errors."""

    def __init__(self, action: FailedAction, asset_id: Id, amount_needed: int):
        """
        Initialize the InsufficientFundsError.

        Args:
            action (FailedAction): The action that failed due to insufficient funds.
            asset_id (Id): The ID of the asset for which funds are insufficient.
            amount_needed (int): The additional amount required to complete the action.
        """
        self.action = action
        self.asset_id = asset_id
        self.amount_needed = amount_needed
        self.message = (
            f"Insufficient funds ({self.action.value} Amount): "
            f"need {self.amount_needed} more units of asset {self.asset_id.to_string()} to {self.action.value.lower()}."
        )
        super().__init__(self.message)

    def __str__(self):
        """Return a string representation of the error."""
        return self.message
