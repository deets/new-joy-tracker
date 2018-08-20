#!/usr/bin/env python3.6
import struct

from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, coroutine, get_event_loop

from pythonosc import osc_message_builder
from pythonosc import udp_client

class Deriver():

    def __init__(self):
        self._last = None


    def feed(self, value):
        res = 0.0
        if self._last is not None:
            res = value - self._last
        self._last = value
        return res


class Asymptoter():

    def __init__(self, decay=0.1):
        self._value = 0.0
        self._decay = decay


    def feed(self, value):
        self._value += value
        self._value -= self._value * self._decay
        return self._value


class Peer(object):
    FORMAT = "<cIHIIIfffhfffB" # START, NAME, SEQUENCE, TIMESTAMP, TEMPERATURE, PRESSURE,
                               # ACC_X, ACC_Y, ACC_Z, TEMP, GYR_X, GYR_Y, GYR_Z
                               # CHECKSUM

    def __init__(self, loop, server, sock, name, client):
        self._loop = loop
        self.name = name
        self._sock = sock
        self._server = server
        self._client = client
        Task(self._peer_loop())

    async def _peer_loop(self):
        packet_length = struct.calcsize(self.FORMAT)
        invalid_count = 0
        pressure_deriver = Deriver()
        pressure_asymptote = Asymptoter()

        while True:
            buf = await self._loop.sock_recv(self._sock, 1024)
            if buf == b'':
                break
            while len(buf) >= packet_length:
                if buf[0] != ord('#'):
                    invalid_count += 1
                    # try & forward the buffer to
                    # the beginning of a potential message
                    if buf.find(b'#') != -1:
                        buf = buf[buf.find(b'#'):]
                        continue
                message = buf[:packet_length]
                buf = buf[packet_length:]
                start, name, seq, timestamp, bmp_temp, pressure, acc_x, acc_y, acc_z, temp, g_x, g_y, g_z, checksum = \
                  struct.unpack(self.FORMAT, message)

                pressure /= 25600.0
                pressure_d = pressure_deriver.feed(pressure)
                pressure_a = pressure_asymptote.feed(pressure_d)

                print("{: > 10.3f} {: > 10.3f} {: > 10.3f} {: > 10.3f} {: > 10.3f} {: > 10.3f} {}".format(
                    pressure,
                    pressure_d,
                    pressure_a,
                    g_x, g_y, g_z,
                    invalid_count
                    )
                )
                b = osc_message_builder.OscMessageBuilder("/filter")
                b.add_arg(pressure)
                b.add_arg(pressure_d)
                b.add_arg(pressure_a)

                self._client.send(b.build())


class Server(object):
    def __init__(self, port, client):
        self._loop = get_event_loop()
        self._serv_sock = socket()
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(('', port))
        self._serv_sock.listen(5)
        self._peers = []
        self._client = client
        Task(self._server())

    def remove(self, peer):
        self._peers.remove(peer)
        self.broadcast('Peer %s quit!\n' % (peer.name,))

    def broadcast(self, message):
        for peer in self._peers:
            peer.send(message)

    async def _server(self):
        while True:
            peer_sock, peer_name = await self._loop.sock_accept(self._serv_sock)
            peer_sock.setblocking(0)
            peer = Peer(self._loop, self, peer_sock, peer_name, self._client)
            print(peer, "created")
            self._peers.append(peer)


    def run_forever(self):
        self._loop.run_forever()


def main():
    client = udp_client.UDPClient('192.168.0.102', 5005)
    server = Server(5000, client)
    server.run_forever()

if __name__ == '__main__':
    main()
