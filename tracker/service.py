import ast

from aiohttp import web

from tracker import RedBlackTree
from random import sample

MAX_PEERS = 10


def get_app(tree_dict, loop):
    def get_tree(hash) -> RedBlackTree:
        if hash not in tree_dict:
            tree_dict[hash] = RedBlackTree()
        return tree_dict[hash]

    async def children(request):
        tree = get_tree(request.match_info['hash'])
        value = request.rel_url.query.get('value', None)
        if value:
            value = ast.literal_eval(value)
            node = tree.find_node(value)
            if node:
                return web.json_response(node.children())
        return web.json_response({'Error': 'Value not found in tree'})

    async def peers(request):
        tree = get_tree(request.match_info['hash'])
        values = list(tree)
        size = min(len(values), MAX_PEERS)
        return web.json_response(sample(values, size))

    async def dashboard(request):
        tree = get_tree(request.match_info['hash'])
        node = tree.root
        if node:
            value = node.value
            return web.HTTPFound('http://{}:{}/dashboard'.format(value[0], value[1]))
        return web.json_response({'Error': 'Tree has no root'})

    async def add_node(request):
        tree = get_tree(request.match_info['hash'])
        value = request.rel_url.query.get('value', None)
        if value:
            value = ast.literal_eval(value)
            tree.add(value)
            return web.json_response({'value': value})
        return web.json_response({'Error': 'Value not given'})

    app = web.Application(loop=loop)
    app.add_routes([web.get('/dashboard/{hash}', dashboard),
                    web.get('/add/{hash}', add_node),
                    web.get('/children/{hash}', children),
                    web.get('/peers/{hash}', peers)])
    return app
