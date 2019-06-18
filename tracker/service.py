from aiohttp import web

from tracker.encoder import JSONCustomEncoder
from tracker.service_helper import check_remove, request_to_node, send_distribution, set_scrapes


def get_app(loop, database):

    async def clear(request):
        """ removes all values from the list"""
        database.node_list = []
        print('Database emptied')
        return web.Response(body='OK')

    async def add_node(request):
        """ Add a value to the list """
        node = await request_to_node(request)
        database.add(node)
        distribution = database.distribute()
        send_distribution(loop, distribution)
        set_scrapes(database.node_list)
        print(f'Added: {node}')
        return web.Response(body='OK')

    async def get_distribution(request):
        """ Return the distribution """
        distribution = database.distribute()
        print(f'get_distribution')
        return web.json_response({'distribution': distribution},
                                 dumps=JSONCustomEncoder.encode)

    async def get_list(request):
        """ Return all elements """
        print(f'get_list')
        return web.json_response({'list': database.node_list},
                                 dumps=JSONCustomEncoder.encode)

    async def remove_node(request):
        """ Add a value to the tree. """
        node = await request_to_node(request)
        loop.create_task(check_remove(database, node))
        print(f'Removed: {node}')
        return web.Response(body='OK')

    app = web.Application()
    app.add_routes([web.post('/root/add', add_node),
                    web.post('/root/remove', remove_node),
                    web.get('/root/distribution', get_distribution),
                    web.get('/root/clear', clear),
                    web.get('/root/list', get_list)])
    return app
