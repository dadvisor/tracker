import threading
import time
from ipaddress import ip_address

import requests

SLEEP_TIME = 10


def start_active_thread(server):
    t = ActiveThread(server)
    t.start()


class ActiveThread(threading.Thread):

    def __init__(self, server):
        threading.Thread.__init__(self, name='ActiveThread')
        self.server = server
        self.running = True

    def run(self):
        while self.running:
            try:
                time.sleep(SLEEP_TIME)
                self.validate()
            except Exception as e:
                self.server.logger.error(e)

    def validate(self):
        """Check if every address is still valid"""
        self.server.logger.info('Validating addresses')
        for infohash, data in list(self.server.torrents.items()):
            for peerid, (ip, port) in list(data.items()):
                try:
                    ip = str(ip_address(ip))
                    requests.get('http://{}:{}/ip'.format(ip, port)).text()
                except Exception:
                    self.server.logger.info('Removing address: {}:{}'.format(ip, port))
                    del self.server.torrents[infohash][peerid]
                    if self.server.torrents[infohash] == {}:
                        del self.server.torrents[infohash]
