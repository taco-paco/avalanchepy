from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from avalanchepy.types.primitives.id import Id


class PaginationIndex(BaseModel):
    address: str
    utxo: str


class GetUTXOsRequest(BaseModel):
    addresses: List[str]
    limit: Optional[int] = None
    start_index: Optional[PaginationIndex] = Field(default=None, alias="startIndex")
    source_chain: Optional[str] = Field(default=None, alias="sourceChain")
    encoding: Optional[str] = None


class GetUTXOsResponse(BaseModel):
    num_fetched: int = Field(alias="numFetched")
    utxos: List[str]
    end_index: PaginationIndex = Field(alias="endIndex")
    source_chain: Optional[str] = Field(default=None, alias="sourceChain")
    encoding: str


class GetTimestampeResponse(BaseModel):
    timestamp: str


class IssueTxRequest(BaseModel):
    tx: str = Field(description="is the byte representation of a transaction.")
    encoding: Optional[str] = Field(
        default="hex",
        description="specifies the encoding format for the transaction bytes. Can only be hex when a value is provided",
    )


class IssueTxResponse(BaseModel):
    tx_id: str = Field(alias="txID")


class GetTxStatusRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    tx_id: Annotated[Id, PlainSerializer(lambda id: id.to_string(), return_type=str), Field(alias="txId")]


class GetTxStatusResponse(BaseModel):
    status: Literal["Committed", "Processing", "Dropped", "Dropped"]
