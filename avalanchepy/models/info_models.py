from pydantic import BaseModel, Field


# POP - proof of possession
class NodePOP(BaseModel):
    public_key: str = Field(alias="publicKey")
    proof_of_possession: str = Field(alias="proofOfPossession")


class GetNodeIdResponse(BaseModel):
    node_id: str = Field(alias="nodeID")
    node_pop: NodePOP = Field(alias="nodePOP")


class GetNetworkIdResponse(BaseModel):
    network_id: int = Field(alias="networkID")


class GetBlockchainIdRequest(BaseModel):
    alias: str


class GetBlockchainIdResponse(BaseModel):
    blockchain_id: str = Field(alias="blockchainID")
