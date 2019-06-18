"""

    This is a debug file and does not contain any tests

"""

import asyncio

from tracker.model import Node
from tracker.service_helper import send_post


async def send_post_add(node):
    await send_post('http://35.204.250.252:14100/root/add', node)


async def send_post_remove(node):
    await send_post('http://35.204.250.252:14100/root/remove', node)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(send_post_add(Node('localhost', 14100, True)))
    loop.run_until_complete(send_post_add(Node('ip', 123, False)))
    # loop.run_until_complete(send_post_remove(Node('ip', 123, False)))
