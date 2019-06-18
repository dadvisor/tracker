from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from tracker import get_app, Database

HASH = '1234'


class TestService(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        return get_app(self.loop, Database())

    @unittest_run_loop
    async def test_add_node(self):
        peer = 'localhost', 14100
        resp = await self.client.get('/add/{}/{}:{}'.format(HASH, peer[0], peer[1]))
        assert resp.status == 200

    @unittest_run_loop
    async def test_remove_node(self):
        peer = 'localhost', 14100
        await self.client.get('/add/{}/{}:{}'.format(HASH, peer[0], peer[1]))
        resp = await self.client.get('/remove/{}/{}:{}'.format(HASH, peer[0], peer[1]))
        assert resp.status == 200

    @unittest_run_loop
    async def test_peers(self):
        peer = 'localhost', 14100
        await self.client.get('/add/{}/{}:{}'.format(HASH, peer[0], peer[1]))
        resp = await self.client.get('/peers/{}'.format(HASH))
        assert resp.status == 200
