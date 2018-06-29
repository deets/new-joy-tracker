# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import socket
import threading
import struct
from collections import namedtuple

PORT = 5000

Message = namedtuple("Message", "name seq timestamp temperature pressure")

class Hub:
    FORMAT = "<IHIII" # NAME, SEQUENCE, TIMESTAMP, TEMPERATURE, PRESSURE

    def __init__(self, port=PORT):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.sndbuf_size)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self._socket.bind(("", port))


    def start(self):
        t = threading.Thread(target=self._read)
        t.daemon = True
        t.start()


    def _read(self):
        while True:
            datagram = self._socket.recv(1024)
            name, seq, ts, temp, pressure = struct.unpack(self.FORMAT, datagram)
            name = b"".join(struct.unpack("ssss", struct.pack("<I", name)))
            msg = Message(
                name,
                seq,
                ts,
                self._convert_temp(temp),
                self._convert_pressure(pressure),
            )
            print(msg)


    def _convert_temp(self, temp):
        return temp / 100.0


    def _convert_pressure(self, pressure):
        return pressure / 25600.0
