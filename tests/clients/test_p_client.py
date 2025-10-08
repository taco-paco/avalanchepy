from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from avalanchepy.clients.errors import ClientError, FormatError
from avalanchepy.clients.p_client import PClient
from avalanchepy.json_provider.errors import JsonProviderError, ResponseValidationError
from avalanchepy.json_provider.json_provider import JsonProvider
from avalanchepy.models.p_models import (
    GetTimestampeResponse,
    GetUTXOsRequest,
    GetUTXOsResponse,
    PaginationIndex,
)
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.errors import DeserializationError
from tests.conftest import UTXO_1_STR


@pytest.fixture
def mock_provider():
    provider = MagicMock(spec=JsonProvider)
    return provider


@pytest.fixture
def p_client(mock_provider):
    with patch("avalanchepy.clients.base_client.JsonProvider", return_value=mock_provider):
        return PClient("http://testurl.com")


@pytest.fixture
def mock_utxos_response():
    # Return a mock GetUTXOsResponse object
    return GetUTXOsResponse(
        numFetched=5,
        utxos=[UTXO_1_STR, UTXO_1_STR],
        endIndex=PaginationIndex(
            address="P-avax18jma8ppw3nhx5r4ap8clazz0dps7rv5ukulre5",
            utxo="kbUThAUfmBXUmRgTpgD6r3nLj7rJUGho6xyht5nouNNypH45j",
        ),
        encoding="hex",
    )


@pytest.fixture
def mock_timestamp_response():
    # Return a mock GetTimestampeResponse object
    return GetTimestampeResponse(timestamp="2023-10-01T00:00:00")


def test_get_utxos_success(p_client, mock_provider, mock_utxos_response):
    mock_provider.call_method.return_value = mock_utxos_response

    request = GetUTXOsRequest(addresses=["test_address"])
    result = p_client.get_utxos(request)

    assert len(result) == 2
    assert isinstance(result[0], Utxo)
    assert isinstance(result[1], Utxo)


def test_get_utxos_deserialization_error(p_client, mock_provider, mock_utxos_response):
    mock_provider.call_method.return_value = mock_utxos_response
    with patch(
        "avalanchepy.types.avax.utxo.Utxo.deserialize", side_effect=DeserializationError("Deserialization failed")
    ):
        request = GetUTXOsRequest(addresses=["test_address"])
        with pytest.raises(FormatError):
            p_client.get_utxos(request)


def test_get_utxos_json_provider_error(p_client, mock_provider):
    mock_provider.call_method.side_effect = JsonProviderError("Provider error")

    request = GetUTXOsRequest(addresses=["test_address"])
    with pytest.raises(ClientError):
        p_client.get_utxos(request)


def test_get_utxos_response_validation_error(p_client, mock_provider):
    mock_provider.call_method.side_effect = ResponseValidationError("Validation error")

    request = GetUTXOsRequest(addresses=["test_address"])
    with pytest.raises(FormatError):
        p_client.get_utxos(request)


def test_get_timestamp_success(p_client, mock_provider, mock_timestamp_response):
    mock_provider.call_method.return_value = mock_timestamp_response
    result = p_client.get_timestamp()
    assert result == datetime(2023, 10, 1, 0, 0, 0)


def test_get_timestamp_json_provider_error(p_client, mock_provider):
    mock_provider.call_method.side_effect = JsonProviderError("Provider error")
    with pytest.raises(ClientError):
        p_client.get_timestamp()
