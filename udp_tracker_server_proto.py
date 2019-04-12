import asyncio
import struct
from datetime import datetime, timedelta
from ipaddress import ip_address
from random import randint, sample


class UdpTrackerServerProto(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
        self.connection_lost_received = asyncio.Event()
        self.transport = None

    def error(self, tid, msg):
        return struct.pack('!II', 3, tid) + msg

    def process_connect(self, addr, connid, tid):
        self.server.logger.info('Received connect message.')
        if connid == 0x41727101980:
            connid = randint(0, 0xffffffffffffffff)
            self.server.connids[connid] = datetime.now()
            self.server.activity[addr] = datetime.now()
            return struct.pack('!IIQ', 0, tid, connid)
        else:
            return self.error(tid, 'Invalid protocol identifier.'.encode('utf-8'))

    def process_announce(self, addr, connid, tid, data):
        self.server.logger.info('Received announce message.')
        fmt = '!20s20sIIIIH'
        size = struct.calcsize(fmt)

        if len(data) > size:
            data = data[:size]
        ih, peerid, ev, ip, k, num_want, port = struct.unpack(fmt, data)

        # make sure the provided connection identifier is valid
        timestamp = self.server.connids.get(connid, None)
        last_valid = datetime.now() - timedelta(seconds=self.server.connid_valid_period)
        if not timestamp:
            return self.error(tid, 'Invalid connection identifier.'.encode('utf-8'))
        elif timestamp < last_valid:
            del self.server.connids[connid]
            return self.error(tid, 'Old connection identifier.'.encode('utf-8'))
        else:
            self.server.activity[connid] = datetime.now()

            # send the event to the tracker
            self.server.announce(ih, peerid, ev, ip, port)
            self.server.logger.info('{}, {}'.format(ip, port))
            self.server.logger.info(self.server.torrents.get(ih, {}).values())
            all_peers = [i for i in self.server.torrents.get(ih, {}).values() if i != (ip, port)]

            # we can't give more peers than we've got
            num_want = min(num_want, len(all_peers))
            peers = sample(all_peers, num_want)

            # now pack the (ip, port) pairs
            peers = b''.join(
                (ip_address(p[0]).packed + p[1].to_bytes(length=2, byteorder='big'))
                for p in peers)

            # construct and return the response
            return struct.pack('!II', 1, tid) + peers

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.connection_lost_received.set()

    def datagram_received(self, data, addr):
        if len(data) < 16:
            self.server.logger.warning('Datagram smaller than 16 bytes.')
            return

        connid, action, tid = struct.unpack('!QII', data[:16])
        if action == 0:
            resp = self.process_connect(addr, connid, tid)
            self.transport.sendto(resp, addr)
        elif action == 1:
            resp = self.process_announce(addr, connid, tid, data[16:])
            self.transport.sendto(resp, addr)

    def error_received(self, exc):
        self.server.logger.info('Error received:'.format(exc))
