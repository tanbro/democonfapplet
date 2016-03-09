# -*- encoding: utf-8 -*-

"""
Client's JSON-RPC over WebSocket HTTP handler
"""

import logging
from functools import partial
from asyncio import iscoroutinefunction, iscoroutine, get_event_loop

from aiohttp import web, MsgType

from . import jsonrpc

__all__ = ['handler']


async def handler(request):
    logger = logging.getLogger(__name__)
    ws = None
    client_id = 1  # 测试嘛，只允许一个WS连接！！！
    try:
        if client_id in request.app['websocket_clients']:
            raise web.HTTPConflict(text='测试嘛，只允许一个WS连接！')
        request.app['websocket_clients'][client_id] = ws
        # 建立 WebSocket 连接!
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        # websocket UPDATE 完成！
        async for msg in ws:
            if msg.tp == MsgType.pong:
                ws.send_str('PONG!')
            elif msg.tp == MsgType.ping:
                ws.send_str('PING!')
            # Text Message
            elif msg.tp == MsgType.text:
                # parse JSON-RPC in an executor, then async wait for the result
                parsed = None
                send_text = ''
                try:
                    parsed = jsonrpc.parse(msg.data)
                except (
                        jsonrpc.InvalidRequestError,
                        jsonrpc.InvalidParamsError,
                        jsonrpc.MethodNotFoundError
                ) as exc:
                    if exc.id is not None:  # responsible JSON-RPC parse errors.
                        send_text = exc.json_string
                except jsonrpc.Error:
                    pass  # ignore un-responsible JSON-RPC parse errors.
                #
                # Request Incoming
                if isinstance(parsed, jsonrpc.Request):
                    try:
                        # get callable object
                        if isinstance(parsed.stub.callable_object, type):
                            # RPC implementations of Classes will be constructed with parameters:
                            # Loop, Session, Client ...
                            rpc_cls_obj = parsed.stub.callable_object(request.app.loop, client_id)
                            execute_obj = getattr(rpc_cls_obj, 'execute')
                        else:
                            # RPC implementations of functions do not have any additional parameters!
                            # It's not advised!
                            execute_obj = parsed.stub.callable_object
                        if iscoroutinefunction(execute_obj) or iscoroutine(execute_obj):
                            # execute in loop
                            result = await execute_obj(*parsed.args, **parsed.kwargs)
                        else:
                            # execute in pool, and wait in loop!
                            result = await request.app.loop.run_in_executor(
                                None, partial(execute_obj, *parsed.args, **parsed.kwargs))
                        # 是否要发送RPC执行结果？
                        if not parsed.stub.is_notification:
                            send_text = jsonrpc.make_response_text(parsed.id, result)
                    except jsonrpc.Error as exc:
                        logger.exception('JSON-RPC error response')
                        if (not parsed.stub.is_notification) and parsed.id:
                            exc.id = parsed.id
                            send_text = exc.json_string
                    except Exception as exc:
                        logger.exception('JSON-RPC executing error')
                        if (not parsed.stub.is_notification) and parsed.id:
                            send_text = jsonrpc.InternalError(parsed.id, str(exc)).json_string
                # Response Incoming
                elif isinstance(parsed, jsonrpc.Response):
                    # TODO: Incoming Response
                    pass
                # Error Incoming
                elif isinstance(parsed, jsonrpc.ErrorResponse):
                    # TODO: Incoming Error
                    pass
                #
                # send text whatever
                if send_text:
                    ws.send_str(send_text)
            #
            # Error Message
            elif msg.tp == MsgType.error:
                logger.error('ws: WebSocket connection closed with exception %s', ws.exception())
    except web.HTTPError:
        raise
    except:
        logger.exception('')
    finally:
        if client_id:
            request.app['websocket_clients'].pop(client_id, None)
        if ws:
            try:
                await ws.close()
            except RuntimeError:
                pass  # Raises:	RuntimeError – if connection is not started or closing
    return ws
