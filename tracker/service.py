from aiohttp import web

from tracker import RedBlackTree


def get_app(tree_dict, loop):
    def get_tree(hash) -> RedBlackTree:
        if hash not in tree_dict:
            tree_dict[hash] = RedBlackTree()
        return tree_dict[hash]

    async def peers(request):
        """ Returns a list of peers """
        tree = get_tree(request.match_info['hash'])
        return web.json_response(list(tree))

    async def dashboard(request):
        """ Returns the grafana dashboard """
        tree = get_tree(request.match_info['hash'])
        node = tree.root
        if node:
            value = node.value
            return web.HTTPFound('http://{}:{}/dadvisor/dashboard'.format(value[0], value[1]))
        return web.json_response({'Error': 'Tree has no root'})

    async def add_node(request):
        """ Add a value to the tree.
        Example: /add/<hash>/ip:port"""
        tree = get_tree(request.match_info['hash'])
        peer = request.match_info['peer']
        host, port = peer.split(':')
        tree.add((host, port))
        return web.json_response({'value': (host, port)})

    async def remove_node(request):
        """ Add a value to the tree.
        Example: /remove/<hash>/ip:port"""
        tree = get_tree(request.match_info['hash'])
        peer = request.match_info['peer']
        host, port = peer.split(':')
        tree.remove((host, port))
        return web.json_response({'value': (host, port)})

    async def node_info(request):
        """ Returns the children of a given value.
        Example: /node_info/<hash>/<ip>:<port>"""
        tree = get_tree(request.match_info['hash'])
        peer = request.match_info['peer']
        host, port = peer.split(':')
        node = tree.find_node((host, port))
        if node:
            parent = node.parent.value if node.parent else None
            children = [value for value in node.children().values() if value]
            return web.json_response({'parent': parent, 'children': children})
        return web.json_response({'Error': 'Value not found in tree'})

    app = web.Application(loop=loop)
    app.add_routes([web.get('/dashboard/{hash}', dashboard),
                    web.get('/add/{hash}/{peer}', add_node),
                    web.get('/remove/{hash}/{peer}', remove_node),
                    web.get('/peers/{hash}', peers),
                    web.get('/node_info/{hash}/{peer}', node_info)])
    return app
