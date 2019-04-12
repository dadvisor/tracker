import asyncio
import struct
from datetime import datetime, timedelta
from ipaddress import ip_address
from random import randint, sample


class UdpTrackerServerProto(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
        self.logger = server.logger
        self.connection_lost_received = asyncio.Event()
        self.transport = None

    def error(self, tid, msg):
        return struct.pack('!II', 3, tid) + msg

    def process_connect(self, addr, connid, tid, data):
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

        # remove extensions
        if len(data) > 82:
            data = data[:82]

        # parse the request
        ih, peerid, dl, left, ul, ev, ip, k, num_want, port = struct.unpack('!20s20sQQQIIIIH', data)

        # use the ip address in the message if it's provided
        if ip == 0:
            ip = addr[0]

        # make sure the provided connection identifier is valid
        timestamp = self.server.connids.get(connid, None)
        last_valid = datetime.now() - timedelta(seconds=self.server.connid_valid_period)
        if not timestamp:
            # we didn't generate that connection identifier
            return self.error(tid, 'Invalid connection identifier.'.encode('utf-8'))
        elif timestamp < last_valid:
            # we did generate that identifier, but it's too
            # old. remove it and send an error.
            del self.server.connids[connid]
            return self.error(tid, 'Old connection identifier.'.encode('utf-8'))
        else:
            self.server.activity[connid] = datetime.now()

            # send the event to the tracker
            self.server.announce(ih, peerid, dl, left, ul, ev, ip, port)

            # get all peers for this torrent
            all_peers = self.server.torrents.get(ih, {}).values()

            # count all peers that have announced "completed". these
            # are the seeders. the rest are leechers.
            seeders = sum(1 for _, _, _, _, _, completed in all_peers
                          if completed)
            leechers = len(all_peers) - seeders

            # we're not interested in anything but (ip, port) pairs
            # anymore
            all_peers = [(ip, port) for ip, port, dl, left, ul, c in all_peers]

            # remove this peer from the list
            all_peers = [i for i in all_peers if i != addr]

            # we can't give more peers than we've got
            num_want = min(num_want, len(all_peers))

            # get a random sample from the peers
            peers = sample(all_peers, num_want)

            # now pack the (ip, port) pairs
            peers = b''.join(
                (ip_address(p[0]).packed + p[1].to_bytes(length=2, byteorder='big'))
                for p in peers)

            # construct and return the response
            return struct.pack(
                '!IIII',
                1, tid, leechers, seeders) + peers

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.connection_lost_received.set()

    def datagram_received(self, data, addr):
        if len(data) < 16:
            self.logger.warning('Datagram smaller than 16 bytes.')
            return

        connid, action, tid = struct.unpack('!QII', data[:16])
        resp = {
            0: self.process_connect,
            1: self.process_announce
        }.get(action, lambda a, c, t, d: None)(addr, connid,
                                               tid, data[16:])

        if resp:
            self.transport.sendto(resp, addr)

    def error_received(self, exc):
        self.logger.info('Error received:'.format(exc))
