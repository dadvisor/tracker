import asyncio
import json

import aiohttp

from tracker import log
from tracker.model import Node
from tracker.util import send_get, set_scrapes, send_post


def _get_name(node):
    return f'http://{node.ip}:{node.port}/dadvisor'


async def _get_peer_info(node):
    async with aiohttp.ClientSession() as session:
        async with session.get(_get_name(node) + '/get_info') as resp:
            return await resp.json()


async def request_to_node(request):
    """ Helper function to retrun a Node-object from the json data in the POST request"""
    data = json.loads(await request.json())
    node = data.get('node')
    return Node(node.get('ip'), int(node.get('port')), node.get('is_super_node'))


async def check_remove(loop, database, node):
    """
    Verify whether the node cannot be reached
    """
    for i in range(10):
        await asyncio.sleep(6)
        if await send_get(f'http://{node.ip}:{node.port}/dadvisor/get_info'):
            return
    database.remove(node)
    send_distribution(loop, database.distribute())
    set_scrapes(database.node_list)
    log.info(f'Removed {node}')


async def check_online(loop, database):
    """
    Perform a heartbeat check every 60 seconds and remove the nodes that are offline
    """
    while True:
        await asyncio.sleep(60)
        for node in database.node_list:
            loop.create_task(check_remove(loop, database, node))


def send_distribution(loop, distribution):
    for super_node, node_list in distribution:
        loop.create_task(send_post(
            f'http://{super_node.ip}:{super_node.port}/dadvisor/set_distribution',
            {'nodes': node_list}))
