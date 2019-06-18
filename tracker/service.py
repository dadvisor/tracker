from aiohttp import web

from tracker.service_helper import check_remove, request_to_node, send_distribution, set_scrapes


def get_app(loop, database):
    async def add_node(request):
        """ Add a value to the tree """
        node = await request_to_node(request)
        if database.add(node):
            distribution = database.distribute()
            send_distribution(loop, distribution)
            set_scrapes(database.node_list)
        print(f'Add: {node}')
        return web.Response(body='OK')

    async def get_distribution(request):
        """ Return the distribution """
        distribution = database.distribute()
        print(f'distribution')
        return web.json_response({'distribution': distribution})

    async def remove_node(request):
        """ Add a value to the tree. """
        node = await request_to_node(request)
        loop.create_task(check_remove(database, node))
        print(f'Remove: {node}')
        return web.Response(body='OK')

    app = web.Application()
    app.add_routes([web.post('/root/add', add_node),
                    web.post('/root/remove', remove_node),
                    web.get('/root/distribution', get_distribution)])
    return app
