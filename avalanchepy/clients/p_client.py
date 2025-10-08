import hashlib
from datetime import datetime
from typing import List, TypeVar

from pydantic import BaseModel

from avalanchepy.clients.base_client import BaseClient
from avalanchepy.clients.errors import FormatError
from avalanchepy.contants import RpcPath
from avalanchepy.models.p_models import (
    GetTimestampeResponse,
    GetTxStatusRequest,
    GetTxStatusResponse,
    GetUTXOsRequest,
    GetUTXOsResponse,
    IssueTxRequest,
    IssueTxResponse,
)
from avalanchepy.types.avax.signed_tx import SignedTx
from avalanchepy.types.avax.utxo import Utxo
from avalanchepy.types.codecs import PVM_CODEC
from avalanchepy.types.errors import DeserializationError
from avalanchepy.types.primitives.id import Id
from avalanchepy.types.utils import pack_codec_direct

T = TypeVar("T", bound=BaseModel)


class PClient(BaseClient):
    def __init__(self, url: str):
        super().__init__(url, RpcPath.P_CHAIN)

    def get_utxos(self, request: GetUTXOsRequest) -> List[Utxo]:
        Ox_OFFSET = 2
        CODEC_OFFSET = 2

        # exported utxos also shall be imported.
        # To get exported but not yet imported utxos, uncomment below.
        # Tho those can't be used for staking
        # request.source_chain = "C"
        result = self._wrapped_call(GetUTXOsResponse, "platform.getUTXOs", request)
        try:
            prepared_utxos: List[bytes] = [bytes.fromhex(el[Ox_OFFSET:])[CODEC_OFFSET:] for el in result.utxos]
            return [Utxo.deserialize(data, PVM_CODEC)[0] for data in prepared_utxos]
        except DeserializationError as e:
            raise FormatError(e) from e
        except Exception as e:
            raise FormatError(e) from e

    def get_timestamp(self) -> datetime:
        response = self._wrapped_call(GetTimestampeResponse, "platform.getTimestamp")
        try:
            return datetime.fromisoformat(response.timestamp)
        except Exception as e:
            raise FormatError(e) from e

    def issue_tx(self, signed_transaction: SignedTx) -> str:
        data = pack_codec_direct(PVM_CODEC, signed_transaction)
        checksum = hashlib.sha256(data).digest()[-4:]
        data += checksum

        data_hex = "0x" + data.hex()
        response = self._wrapped_call(IssueTxResponse, "platform.issueTx", IssueTxRequest(tx=data_hex))
        return response.tx_id

    def get_tx_status(self, tx_id: Id) -> GetTxStatusResponse:
        return self._wrapped_call(GetTxStatusResponse, "platform.getTxStatus", GetTxStatusRequest(tx_id=tx_id))
