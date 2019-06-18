"""

    This is a debug file and does not contain any tests

"""

import asyncio
import json

import aiohttp

from tracker.database import Node


async def send_post_add(node):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:15000/root/add',
                                json=json.dumps(node.to_json())) as resp:
            print(await resp.text())


async def send_post_remove(node):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:15000/root/remove',
                                json=json.dumps(node.to_json())) as resp:
            print(await resp.text())


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(send_post_add(Node('localhost', 14100, True)))
    loop.run_until_complete(send_post_add(Node('ip', 123, False)))
    loop.run_until_complete(send_post_remove(Node('ip', 123, False)))
