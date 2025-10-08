from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from avalanchepy.types.primitives.id import Id


class GetAssetDescriptionRequest(BaseModel):
    asset_id: str = Field(alias="assetID")


class GetAssetDescriptionResponse(BaseModel):
    asset_id: Annotated[
        Id, BeforeValidator(lambda s: Id.from_string(s), json_schema_input_type=str), Field(alias="assetID")
    ]
    name: str
    symbol: str
    denomination: int
