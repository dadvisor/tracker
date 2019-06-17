import asyncio
import os

from aiohttp import web

from tracker.service import get_app
from tracker.tests import TestService


def run_forever():
    loop = asyncio.new_event_loop()
    app = get_app(loop)
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
