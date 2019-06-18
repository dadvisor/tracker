import json

import aiohttp

from tracker import log
from tracker.model.encoder import JSONCustomEncoder

FILENAME = '/prometheus.json'


async def send_post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=json.dumps(data, cls=JSONCustomEncoder))
        return True
    except Exception as e:
        log.error(e)
    return False


async def send_get(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.text()
    except Exception as e:
        log.error(e)
    return None


def set_scrapes(nodes):
    """ Set a line with federation information. Prometheus is configured in
            such a way that it reads this file. """
    try:
        with open(FILENAME, 'r') as file:
            old_data = file.read()
    except FileNotFoundError:
        old_data = ''

    super_node_list = []
    for node in [node for node in nodes if node.is_super_node]:
        super_node_list.append(f'{node.ip}:{node.port}')

    data = [{"labels": {"job": "federate"}, "targets": super_node_list}]
    new_data = json.dumps(data) + '\n'

    if old_data != new_data:
        with open(FILENAME, 'w') as file:
            file.write(new_data)
