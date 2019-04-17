import asyncio

import aiohttp

SLEEP_TIME = 10


async def validate(tree_dict):
    while True:
        await asyncio.sleep(SLEEP_TIME)
        await iterate_tree(tree_dict)


async def iterate_tree(tree_dict):
    for tree in tree_dict.values():
        for value in tree:
            try:
                await check_alive(value[0], value[1])
            except Exception:
                tree.remove(value)
                print('Removing value: {}:{}'.format(value[0], value[1]))


async def check_alive(address, port):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://{}:{}/ip'.format(address, port)) as resp:
            return await resp.json()
