import asyncio

from tracker_client import TrackerClient


async def announce():
    client = TrackerClient(announce_uri='udp://0.0.0.0:6969', loop=loop)
    await client.start()
    peers = await client.announce(
        b'dfasfa',  # infohash
        10000,  # downloaded
        40000,  # left
        5000,  # uploaded
        0,  # event (0=none)
        120  # number of peers wanted
    )
    client.logger.info('Peers: {}'.format(peers))
    try:
        # sleep(10)
        client.logger.info('Stopping connection')
        data = await client.announce(
            b'fjdals',  # infohash
            10000,  # downloaded
            40000,  # left
            5000,  # uploaded
            3,  # event (0=none)
            120  # number of peers wanted
        )
        client.logger.info(data)
    except Exception as e:
        client.logger.error(e)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(announce())
