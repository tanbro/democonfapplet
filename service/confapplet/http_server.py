# -*- encoding: utf-8 -*-

"""
Async IO HTTP Server
"""

import logging
import asyncio
from aiohttp import web

from . import conf
from . import jsonrpc_handler

__all__ = ['start_server', 'stop_server', 'get_app']

server = None
application = None
handler = None


def start_server(loop):
    get_logger().info('create_server: loop=%s', loop)
    global server
    global application
    global handler
    application = web.Application(loop=loop)
    application['websocket_clients'] = dict()
    application.on_shutdown.append(shutdown_websocket)
    application.router.add_route('GET', '/', jsonrpc_handler.handler)
    handler = application.make_handler()
    fut = loop.create_server(handler, conf.HTTP_ADDRESS, conf.HTTP_PORT)
    server = loop.run_until_complete(fut)
    get_logger().debug('Web Server serving on %s', server.sockets[0].getsockname())


def stop_server(loop):
    get_logger().info('stop_server: loop=%s', loop)
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.run_until_complete(application.shutdown())
    loop.run_until_complete(handler.finish_connections(60.0))
    loop.run_until_complete(application.cleanup())


async def shutdown_websocket(app):
    # remove app's client RPC websocket dict
    websocket_clients = app['websocket_clients']
    app['websocket_clients'] = {}
    fs = []
    for ws in websocket_clients.values():
        fs.append(ws.close())
    if fs:
        await asyncio.wait(fs)


def get_app():
    return application


def get_logger():
    return logging.getLogger(__name__)
