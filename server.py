import asyncio

from tracker_server import TrackerServer

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    tracker = TrackerServer(local_addr=('0.0.0.0', 6969), loop=loop)
    asyncio.ensure_future(tracker.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(tracker.stop())
