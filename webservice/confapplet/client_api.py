from . import jsonrpc
from .utils import *
from . import ytx

RpcAction = jsonrpc.ServerStub.rpc_class


@RpcAction()
class CreateConf(BaseRpcImpl, LoggerMixin):
    async def execute(self):
        res = ytx.ivr_invoke('createconf', 'CreateConf')
        return res['confid']
