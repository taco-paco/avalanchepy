from avalanchepy.clients.base_client import BaseClient
from avalanchepy.contants import RpcPath
from avalanchepy.models.x_models import (
    GetAssetDescriptionRequest,
    GetAssetDescriptionResponse,
)
from avalanchepy.types.primitives.id import Id


class XClient(BaseClient):
    def __init__(self, url: str):
        super().__init__(url, RpcPath.X_CHAIN)

    def get_asset_description(self, asset_id: str = "AVAX") -> Id:
        request = GetAssetDescriptionRequest(assetID=asset_id)
        return self._wrapped_call(GetAssetDescriptionResponse, "avm.getAssetDescription", request).asset_id
