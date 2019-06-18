import asyncio
import os

from aiohttp import web

from tracker.model import Database
from tracker.log import log
from tracker.service import get_app
from tracker.service_helper import check_online


def run_forever():
    loop = asyncio.new_event_loop()
    database = Database()
    app = get_app(loop, database)
    loop.create_task(run_app(app))
    loop.create_task(check_online(loop, database))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        log.info('Stopping loop')
    finally:
        loop.close()


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 14105))
    log.info(f'Running forever on port {port}')
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
