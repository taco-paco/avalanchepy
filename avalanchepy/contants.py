from enum import Enum

from avalanchepy.types.primitives.id import ID_LEN, Id

PRIMARY_NETWORK_ID = Id(value=bytes(ID_LEN * [0]))


class RpcPath(str, Enum):
    P_CHAIN = ("/ext/bc/P",)
    X_CHAIN = ("/ext/bc/X",)
    C_CHAIN = ("/ext/bc/C/avax",)
    INFO_CHAIN = ("/ext/info",)
