from typing import Tuple, TypeVar

from pydantic import BaseModel

from avalanchepy.clients.base_client import BaseClient
from avalanchepy.clients.errors import FormatError
from avalanchepy.contants import RpcPath
from avalanchepy.models.info_models import (
    GetBlockchainIdRequest,
    GetBlockchainIdResponse,
    GetNetworkIdResponse,
    GetNodeIdResponse,
    NodePOP,
)
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.node_id import NodeId

T = TypeVar("T", bound=BaseModel)


class InfoClient(BaseClient):
    def __init__(self, url: str):
        super().__init__(url, RpcPath.INFO_CHAIN)

    def get_node_id(self) -> Tuple[NodeId, NodePOP]:
        response = self._wrapped_call(GetNodeIdResponse, "info.getNodeID")
        try:
            node_id = NodeId.from_string(response.node_id)
            return node_id, response.node_pop
        except Exception as e:
            raise FormatError(e) from e

    def get_network_id(self) -> int:
        response = self._wrapped_call(GetNetworkIdResponse, "info.getNetworkID")
        return response.network_id

    def get_blockchain_id(self, request: GetBlockchainIdRequest) -> Id:
        response = self._wrapped_call(GetBlockchainIdResponse, "info.getBlockchainID", request)
        try:
            return Id.from_string(response.blockchain_id)
        except Exception as e:
            raise FormatError(e) from e
