import asyncio
import json

import aiohttp

from tracker.database import Node


async def send_post_add(node):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:14100/add/hash',
                                json=json.dumps(node.to_json())) as resp:
            print(await resp.text())


async def send_post_remove(node):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:14100/remove/hash',
                                json=json.dumps(node.to_json())) as resp:
            print(await resp.text())


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(send_post_add(Node('ip', 1234, True)))
    loop.run_until_complete(send_post_add(Node('ip', 123, False)))
    loop.run_until_complete(send_post_remove(Node('ip', 123, False)))
