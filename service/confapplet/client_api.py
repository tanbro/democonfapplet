import asyncio

from aiohttp import web

from . import jsonrpc
from .utils import *

RpcAction = jsonrpc.ServerStub.rpc_class


@RpcAction()
class CreateConf(BaseRpcImpl, LoggerMixin):
    async def execute(self):
        pass
