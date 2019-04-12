import asyncio
import logging
import os
import sys
from collections import defaultdict
from urllib.parse import urlparse

from udp_tracker_client_proto import UdpTrackerClientProto


class TrackerClient:
    def __init__(self, announce_uri, max_retransmissions=8, loop=None):
        self.logger = logging.getLogger(__name__)

        scheme, netloc, _, _, _, _ = urlparse(announce_uri)
        if scheme != 'udp':
            raise ValueError('Tracker scheme not supported: {}'.format(scheme))
        if ':' not in netloc:
            self.logger.info('Port not specified in announce URI. Assuming 80.')
            tracker_host, tracker_port = netloc, 80
        else:
            tracker_host, tracker_port = netloc.split(':')
            tracker_port = int(tracker_port)

        self.server_addr = tracker_host, tracker_port
        self.transport = None
        self.proto = None
        self.max_retransmissions = max_retransmissions
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.allowed_callbacks = ['connected', 'announced']
        self.connid_valid_period = 60
        self.callbacks = defaultdict(list)
        self.connid = None
        self.connid_timestamp = None
        self.interval = None
        self.peerid = os.urandom(20)
        self.setup_logging()

    def setup_logging(self):
        formatter = logging.Formatter(
            '%(asctime) -15s - %(levelname) -8s - %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def callback(self, cb, *args):
        if cb not in self.allowed_callbacks:
            raise ValueError('Invalid callback: {}'.format(cb))

        for c in self.callbacks[cb]:
            c(*args)

    def add_callback(self, name, func):
        if name not in self.allowed_callbacks:
            raise ValueError('Invalid callback: {}'.format(name))

        self.callbacks[name].append(func)

    def rm_callback(self, name, func):
        if name not in self.allowed_callbacks:
            raise ValueError('Invalid callback: {}'.format(name))

        self.callbacks[name].remove(func)

    async def start(self):
        self.transport, self.proto = await self.loop.create_datagram_endpoint(
            lambda: UdpTrackerClientProto(self),
            remote_addr=self.server_addr)

    async def stop(self):
        self.transport.close()
        await self.proto.connection_lost_received.wait()

    async def announce(self, infohash, downloaded, left, uploaded, event, num_want=160):
        return await self.proto.announce(infohash, num_want, downloaded, left, uploaded, event)

    async def connect(self):
        return await self.proto.connect()
