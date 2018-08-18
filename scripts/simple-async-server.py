#!/usr/bin/python3.6
import struct

from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, coroutine, get_event_loop

class Peer(object):
    FORMAT = "<IHIIIfffhfff" # NAME, SEQUENCE, TIMESTAMP, TEMPERATURE, PRESSURE,
                             # ACC_X, ACC_Y, ACC_Z, TEMP, GYR_X, GYR_Y, GYR_Z

    def __init__(self, loop, server, sock, name):
        self._loop = loop
        self.name = name
        self._sock = sock
        self._server = server
        Task(self._peer_loop())

    async def _peer_loop(self):
        packet_length = struct.calcsize(self.FORMAT)
        while True:
            buf = await self._loop.sock_recv(self._sock, 1024)
            if buf == b'':
                break
            while len(buf) >= packet_length:
                message = buf[:packet_length]
                buf = buf[packet_length:]
                name, seq, timestamp, bmp_temp, pressure, acc_x, acc_y, acc_z, temp, g_x, g_y, g_z = \
                  struct.unpack(self.FORMAT, message)

                print("{: > 10.3f} {: > 10.3f} {: > 10.3f} {: > 10.3f}".format(pressure, g_x, g_y, g_z))


class Server(object):
    def __init__(self, port):
        self._loop = get_event_loop()
        self._serv_sock = socket()
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(('', port))
        self._serv_sock.listen(5)
        self._peers = []
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
            peer = Peer(self._loop, self, peer_sock, peer_name)
            print(peer, "created")
            self._peers.append(peer)


    def run_forever(self):
        self._loop.run_forever()


def main():
    server = Server(5000)
    server.run_forever()

if __name__ == '__main__':
    main()
