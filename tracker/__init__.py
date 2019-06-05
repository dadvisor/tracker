import asyncio
import os

from aiohttp import web

from tracker.bst import RedBlackTree
from tracker.service import get_app
from tracker.validate import validate


def run_forever():
    tree_dict = {}

    loop = asyncio.new_event_loop()
    app = get_app(tree_dict, loop)

    if os.environ.get('LIFE_CHECK', '0') == '1':
        loop.create_task(validate(tree_dict))
    loop.create_task(run_app(app))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping loop')
    finally:
        loop.close()


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 14100))
    print('Running forever on port {}'.format(port))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
