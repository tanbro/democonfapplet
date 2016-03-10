from . import jsonrpc
from .utils import *
from .ytx import ivr_invoke

RpcAction = jsonrpc.ServerStub.rpc_class


@RpcAction()
class CreateConf(BaseRpcImpl, LoggerMixin):
    async def execute(self) -> dict:
        self.logger.info('')
        res = await ivr_invoke('createconf', 'CreateConf')
        self.logger.info('res=%s', res)
        return res


@RpcAction()
class DismissConf(BaseRpcImpl, LoggerMixin):
    async def execute(self, confid: str) -> dict:
        self.logger.info('>>> confid=%s', confid)
        res = await ivr_invoke('conf', 'DismissConf', params={'confid': confid}, confid=confid)
        self.logger.info('<<< res=%s', res)
        return res


@RpcAction()
class QueryConfState(BaseRpcImpl, LoggerMixin):
    async def execute(self, confid: str) -> dict:
        self.logger.info('>>> confid=%s', confid)
        res = await ivr_invoke('conf', 'QueryConfState', params={'confid': confid}, confid=confid)
        self.logger.info('<<< res=%s', res)
        return res


@RpcAction()
class InviteJoinConf(BaseRpcImpl, LoggerMixin):
    async def execute(self, confid: str, number: str) -> dict:
        self.logger.info('>>> confid=%s, number=%s', confid, number)
        res = await ivr_invoke('conf', 'InviteJoinConf', params={'confid': confid}, confid=confid, number=number)
        self.logger.info('<<< res=%s', res)
        return res


@RpcAction()
class QuitConf(BaseRpcImpl, LoggerMixin):
    async def execute(self, confid: str, callid: str) -> dict:
        self.logger.info('>>> confid=%s, callid=%s', confid, callid)
        res = await ivr_invoke('conf', 'InviteJoinConf', params={'confid': confid}, confid=confid, callid=callid)
        self.logger.info('<<< res=%s', res)
        return res
