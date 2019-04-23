import asyncio

from aiohttp import web

from tracker.bst import RedBlackTree
from tracker.service import get_app
from tracker.validate import validate


def run_forever():
    tree_dict = {}

    loop = asyncio.new_event_loop()
    app = get_app(tree_dict, loop)

    # loop.create_task(validate(tree_dict))
    loop.create_task(run_app(app))
    try:
        print('Running forever')
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping loop')
    finally:
        loop.close()


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
