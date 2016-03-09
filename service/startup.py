from sys import exit
from confapplet.__main__ import main

import asyncio

if __name__ == '__main__':
    # exit(main())
    from confapplet.ytx import *

    loop = asyncio.get_event_loop()

    async def run():
        # print('create conf')
        # res = await ivr_invoke('createconf', 'CreateConf')
        # conf_id = res['confid']
        # print('confid:', conf_id)

        conf_id = '60014067'

        print('dismis conf, ', conf_id)
        res = await ivr_invoke('conf', 'DismissConf', params=dict(confid=conf_id), confid=conf_id)
        print(res)

        print('query conf, ', conf_id)
        res = await ivr_invoke('conf', 'QueryConfState', params=dict(confid=conf_id), confid=conf_id)
        print(res)


    loop.run_until_complete(run())
    loop.close()
