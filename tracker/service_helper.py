import asyncio
import json

import aiohttp

from tracker.database import Node


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
    return Node(node.get('ip'), node.get('port'), node.get('is_super_node'))


async def check_remove(database, node):
    """
    Verify whether the node cannot be reached
    """
    for i in range(10):
        await asyncio.sleep(6)
        if await send_get(f'http://{node.ip}:{node.port}/dadvisor/get_info'):
            return
    database.remove(node)
    print(f'Removed {node}')


def send_distribution(loop, distribution):
    for super_node, nodes in distribution:
        ip = super_node['node']['ip']
        port = super_node['node']['port']
        loop.create_task(send_post(
            f'http://{ip}:{port}/dadvisor/set_peers',
            {'nodes': nodes}))


async def send_post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=json.dumps(data))
        return True
    except Exception as e:
        print(e)
    return False


async def send_get(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.text()
    except Exception as e:
        print(e)
    return None
