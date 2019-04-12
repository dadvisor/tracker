import asyncio
import logging
import sys

from udp_tracker_server_proto import UdpTrackerServerProto


class TrackerServer:
    def __init__(self, local_addr=('0.0.0.0', 6969), connid_valid_period=120, loop=None):
        self.local_addr = local_addr
        self.connid_valid_period = connid_valid_period
        self.loop = loop
        self.activity = {}
        self.connids = {}
        self.torrents = {}
        self.transport = None
        self.proto = None
        self.started_up = asyncio.Event()
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        formatter = logging.Formatter(
            '%(asctime) -15s - %(levelname) -8s - %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    async def start(self):
        self.transport, self.proto = await self.loop.create_datagram_endpoint(
            lambda: UdpTrackerServerProto(self),
            local_addr=self.local_addr)
        self.local_addr = self.transport._sock.getsockname()
        self.logger.info('Started listening on {}:{}.'.format(*self.local_addr))
        self.started_up.set()

    async def stop(self):
        self.transport.close()
        await self.proto.connection_lost_received.wait()
        self.logger.info('Tracker stopped.')

    def announce(self, ih, peerid, ev, ip, port):
        if ih not in self.torrents:
            self.logger.info('New info hash encountered: {}'.format(ih.hex()))
            self.torrents[ih] = {}
            self.torrents[ih][peerid] = (ip, port)
        if ih in self.torrents and peerid not in self.torrents[ih]:
            self.logger.debug('New peer encountered: {}'.format(peerid.hex()))
            self.torrents[ih][peerid] = (ip, port)
        if ev == 0:
            # none
            self.logger.info('Regular announce from: {}'.format(peerid.hex()))
            self.torrents[ih][peerid] = (ip, port)
        elif ev == 3:
            # stopped
            self.logger.info('Stop announce from: {}. Removed peer.'.format(peerid.hex()))
            del self.torrents[ih][peerid]
            if self.torrents[ih] == {}:
                del self.torrents[ih]
