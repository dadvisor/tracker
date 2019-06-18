from aiohttp import web

from tracker.service_helper import check_remove, request_to_node, send_distribution


def get_app(loop, database):
    async def add_node(request):
        """ Add a value to the tree.
        Example: /add/<hash>"""
        key = request.match_info['hash']
        node = await request_to_node(request)
        if database.add(key, node):
            distribution = database.distribute(request.match_info['hash'])
            send_distribution(loop, distribution)
        print(f'add/{key}: {node}')
        return web.Response(body='OK')

    async def get_distribution(request):
        key = request.match_info['hash']
        distribution = database.distribute(key)
        print(f'distribution/{key}')
        return web.json_response({'distribution': distribution})

    async def remove_node(request):
        """ Add a value to the tree.
        Example: /remove/<hash>"""
        key = request.match_info['hash']
        node = await request_to_node(request)
        loop.create_task(check_remove(database, key, node))
        print(f'remove/{key}: {node}')
        return web.Response(body='OK')

    app = web.Application()
    app.add_routes([web.post('/root/add/{hash}', add_node),
                    web.post('/root/remove/{hash}', remove_node),
                    web.get('/root/distribution/{hash}', get_distribution)])
    return app
