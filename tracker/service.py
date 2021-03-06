import json

from aiohttp import web

from tracker import log
from tracker.model.encoder import JSONCustomEncoder
from tracker.service_helper import check_remove, request_to_node, send_distribution, set_scrapes


def get_app(loop, database):
    async def clear(request):
        """ removes all values from the list"""
        database.node_list = []
        return web.Response(body='OK')

    async def add_node(request):
        """ Add a value to the list """
        node = await request_to_node(request)
        database.add(node)
        send_distribution(loop, database.distribute())
        set_scrapes(database.node_list)
        log.info(f'Added: {node}')
        return web.Response(body='OK')

    async def get_distribution(request):
        """ Return the distribution """
        distribution = database.distribute()
        return web.json_response(text=json.dumps({'distribution': distribution},
                                                 cls=JSONCustomEncoder))

    async def get_list(request):
        """ Return all elements """
        return web.json_response(text=json.dumps({'list': database.node_list},
                                                 cls=JSONCustomEncoder))

    async def remove_node(request):
        """ Add a value to the tree. """
        node = await request_to_node(request)
        loop.create_task(check_remove(loop, database, node))
        log.info(f'Removed: {node}')
        return web.Response(body='OK')

    app = web.Application()
    app.add_routes([web.post('/root/add', add_node),
                    web.post('/root/remove', remove_node),
                    web.get('/root/distribution', get_distribution),
                    web.get('/root/clear', clear),
                    web.get('/root/list', get_list)])
    return app
