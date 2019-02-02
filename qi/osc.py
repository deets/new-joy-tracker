# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import time
import datetime
import socket

from pythonosc import osc_server
from pythonosc import dispatcher
from pyqtgraph.Qt import QtCore

CONVERTERS = {
    "i": int,
    "f": float,
}

DUMMY_ADDRESS = ("", 12345)


def process_file(filename, sleep=True, speedup=1):
    with open(filename) as inf:
        last_ts = None
        for line in inf:
            ts, _, path, structure, *values = line.split(",")
            ts = datetime.datetime.strptime(ts, "%d.%m.%Y %H:%M:%S")
            if sleep and last_ts is not None:
                time.sleep((ts - last_ts).seconds / speedup)
            last_ts = ts
            yield DUMMY_ADDRESS, path, \
                  [CONVERTERS[kind](v)
                       for v, kind in zip(values, structure)
                  ]


class OSCWorkerBase(QtCore.QObject):

    message = QtCore.pyqtSignal(list, name="message")
    new_path = QtCore.pyqtSignal(str, name="new_path")

    def __init__(self):
        super().__init__()
        self._running = True
        self._path_to_address = {}
        self._server_thread = QtCore.QThread()
        self.moveToThread(self._server_thread)
        self._server_thread.started.connect(self.work)
        self._server_thread.start()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _process_message(self, address, path, args):
        if path not in self._path_to_address:
            self._path_to_address[path] = address
            self.new_path.emit(path)
        self.message.emit([path] + list(args))

    def quit(self):
        self._running = False
        self._server_thread.wait()

    def reset(self, path):
        self._sock.sendto(b"R", self._path_to_address[path])

    def work(self):
        self._work()
        self._server_thread.exit()


class OSCWorker(OSCWorkerBase):

    def __init__(self, destination, port):
        super().__init__()
        self._destination, self._port = destination, port

    def _work(self):
        disp = dispatcher.Dispatcher()
        disp.map("/*", self._got_osc, needs_reply_address=True)
        server = osc_server.BlockingOSCUDPServer(
            (self._destination, self._port),
            disp,
        )
        server.timeout = 1
        while self._running:
            server.handle_request()

    def _got_osc(self, address, path, *args):
        self._process_message(address, path, args)


class FileOSCWorker(OSCWorkerBase):

    def __init__(self, path):
        self._path = path
        super().__init__()

    def _work(self):
        while True:
            for address, path, args in process_file(self._path):
                self._process_message(address, path, args)
                if not self._running:
                    return



if __name__ == '__main__':
    import sys
    for m in process_file(sys.argv[1]):
        print(m)
