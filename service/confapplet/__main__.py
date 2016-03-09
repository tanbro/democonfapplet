# -*- encoding: utf-8 -*-

import sys
import logging.config
import importlib
import asyncio

from . import conf
from . import http_server

logging.config.dictConfig(conf.LOGGING_CONFIG)

# load RPC stub definitions, implementations, Server API entries and actions ...
for name in conf.PRE_IMPORT_MODULES:
    importlib.import_module(name)


def main():
    loop = asyncio.get_event_loop()
    http_server.start_server(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.stop_server(loop)
    loop.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
