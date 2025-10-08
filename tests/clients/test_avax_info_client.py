from unittest.mock import MagicMock, patch

import pytest

from avalanchepy.clients.info_client import InfoClient
from avalanchepy.json_provider.json_provider import JsonProvider
from avalanchepy.models.info_models import (
    GetBlockchainIdRequest,
    GetBlockchainIdResponse,
    GetNetworkIdResponse,
    GetNodeIdResponse,
    NodePOP,
)
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.primitives.node_id import NodeId

NODE_ID_RAW = {
    "nodeID": "NodeID-5mb46qkSBj81k9g9e4VFjGGSbaaSLFRzD",
    "nodePOP": {
        "publicKey": "0x8f95423f7142d00a48e1014a3de8d28907d420dc33b3052a6dee03a3f2941a393c2351e354704ca66a3fc29870282e15",  # noqa: E501
        "proofOfPossession": "0x86a3ab4c45cfe31cae34c1d06f212434ac71b1be6cfe046c80c162e057614a94a5bc9f1ded1a7029deb0ba4ca7c9b71411e293438691be79c2dbf19d1ca7c3eadb9c756246fc5de5b7b89511c7d7302ae051d9e03d7991138299b5ed6a570a98",  # noqa: E501
    },
}


@pytest.fixture
def mock_provider():
    provider = MagicMock(spec=JsonProvider)
    return provider


@pytest.fixture
def info_client(mock_provider):
    with patch("avalanchepy.clients.base_client.JsonProvider", return_value=mock_provider):
        return InfoClient("http://testurl.com")


@pytest.fixture
def mock_node_id_response():
    return GetNodeIdResponse(**NODE_ID_RAW)


@pytest.fixture
def mock_network_id_response():
    return GetNetworkIdResponse(networkID=1)


@pytest.fixture
def mock_blockchain_id_response():
    return GetBlockchainIdResponse(blockchainID="sV6o671RtkGBcno1FiaDbVcFv2sG5aVXMZYzKdP4VQAWmJQnM")


def test_get_node_id_success(info_client, mock_provider, mock_node_id_response):
    mock_provider.call_method.return_value = mock_node_id_response
    node_id, node_pop = info_client.get_node_id()

    assert isinstance(node_id, NodeId)
    assert isinstance(node_pop, NodePOP)


def test_get_network_id_success(info_client, mock_provider, mock_network_id_response):
    mock_provider.call_method.return_value = mock_network_id_response
    network_id = info_client.get_network_id()
    assert network_id == 1


def test_get_blockchain_id_success(info_client, mock_provider, mock_blockchain_id_response):
    mock_provider.call_method.return_value = mock_blockchain_id_response
    request = GetBlockchainIdRequest(alias="X")
    blockchain_id = info_client.get_blockchain_id(request)

    assert isinstance(blockchain_id, Id)
