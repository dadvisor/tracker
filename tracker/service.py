import asyncio

import aiohttp

from aiohttp import web


def get_app(loop):
    peer_dict = {}  # dict of lists

    def get_set(hash) -> []:
        if hash not in peer_dict:
            peer_dict[hash] = set()
        return peer_dict[hash]

    async def get_peers(request):
        """ Returns a list of peers """
        return web.json_response(list(get_set(request.match_info['hash'])))

    async def add_node(request):
        """ Add a value to the tree.
        Example: /add/<hash>/ip:port"""
        peers = get_set(request.match_info['hash'])
        peer = request.match_info['peer']
        host, port = peer.split(':')
        if not (host, port) in peers:
            peers.add((host, port))
            loop.create_task(send_list_to_peers(list(peers)))
        return web.json_response({'value': (host, port)})

    async def remove_node(request):
        """ Add a value to the tree.
        Example: /remove/<hash>/ip:port"""
        peers = get_set(request.match_info['hash'])
        peer = request.match_info['peer']
        host, port = peer.split(':')
        if (host, port) in peers:
            peers.remove((host, port))
            loop.create_task(send_list_to_peers(list(peers)))
        return web.json_response({'value': (host, port)})

    async def send_list_to_peers(peers_list):
        """ Update the peers with the new list """
        async with aiohttp.ClientSession() as session:
            post_tasks = []
            for peer in peers_list:
                host, port = peer
                post_tasks.append(session.post(
                    'http://{}:{}/dadvisor/set_peers'.format(host, port),
                    data={'peers': peers_list}))
            await asyncio.gather(*post_tasks)

    app = web.Application()
    app.add_routes([web.get('/add/{hash}/{peer}', add_node),
                    web.get('/remove/{hash}/{peer}', remove_node),
                    web.get('/peers/{hash}', get_peers)])
    return app
