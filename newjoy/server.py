#!/usr/bin/env python3.6
import struct
import argparse
import time

from functools import partial
from socket import socket, SO_REUSEADDR, SOL_SOCKET, SOCK_DGRAM, AF_INET
from asyncio import Task, coroutine, get_event_loop, DatagramProtocol

import arpreq

from pythonosc import osc_message_builder
from pythonosc import udp_client

DEFAULT_UDP_PORT = 5005
DEFAULT_SERVER_PORT = 5000

from .util import PackageParser

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


FORMAT = "<cIHIIIfffhfffB" # START, NAME, SEQUENCE, TIMESTAMP, TEMPERATURE, PRESSURE,
                           # ACC_X, ACC_Y, ACC_Z, TEMP, GYR_X, GYR_Y, GYR_Z
                           # CHECKSUM


def message_processor(client, visualise_callback):
    packet_length = struct.calcsize(FORMAT)
    parser = PackageParser(packet_length)
    last_timestamp = None

    while True:
        message, name = yield
        timestamp = time.monotonic()
        if last_timestamp is not None:
            packet_diff = timestamp - last_timestamp
        else:
            packet_diff = 0
        last_timestamp = timestamp

        start, name, seq, timestamp, bmp_temp, pressure, acc_x, acc_y, acc_z, temp, g_x, g_y, g_z, checksum = \
          struct.unpack(FORMAT, message)

        pressure /= 25600.0

        print("{: > 10.3f} {: > 10.3f} {: > 10.3f} {: > 10.3f} {} {} {: > 3.2f}".format(
            pressure,
            g_x, g_y, g_z,
            parser.invalid_count,
            seq,
            packet_diff,
            )
        )
        b = osc_message_builder.OscMessageBuilder("/filter")
        b.add_arg(name)
        b.add_arg(pressure)
        b.add_arg(g_x)
        b.add_arg(g_y)
        b.add_arg(g_z)
        b.add_arg(acc_x)
        b.add_arg(acc_y)
        b.add_arg(acc_z)
        b.add_arg(packet_diff)

        message = b.build()
        client.send(message)
        visualise_callback(message)


class NewJoyProtocol(DatagramProtocol):

    def __init__(self, server, *a, **k):
        super().__init__(*a, **k)
        self._server = server
        self._transport = None
        self._ip2name_mapping = {}
        self._unknown_gen = self._generate_unknown_names()


    def connection_made(self, transport):
        self._transport = transport


    def datagram_received(self, data, addr):
        name = self._resolve_name(addr[0])
        self._server._message_processor.send((data, name))


    def _resolve_name(self, ip):
        if ip not in self._ip2name_mapping:
            mac = arpreq.arpreq(ip)
            if mac is None:
                mac = next(self._unknown_gen)
            self._ip2name_mapping[ip] = mac
        return self._ip2name_mapping[ip]


    def _generate_unknown_names(self):
        """
        Generate dummy-names for
        unresolvable mac-addresses
        """
        count = 1
        while True:
            yield f"unknown-{count}"
            count += 1


class Server(object):
    def __init__(self, port, client, visualise_callback):
        self._loop = get_event_loop()
        self._message_processor = message_processor(
            client,
            visualise_callback
        )
        # forward to send yield
        next(self._message_processor)

        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('', port))

        listen = self._loop.create_datagram_endpoint(
            partial(NewJoyProtocol, self),
            sock=sock,
        )
        self._loop.run_until_complete(listen) # returns transport, protocol


    def run_forever(self):
        self._loop.run_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", help="Destination UDP IP")
    parser.add_argument("--port", help="Destination UDP port", default=DEFAULT_UDP_PORT)
    parser.add_argument("-v", "--visualise", help="Send OSC to visualisation server, the format for this argument is ip:port")
    opts = parser.parse_args()

    client = udp_client.UDPClient(opts.destination, opts.port)

    def visualise_callback(_):
        pass

    if opts.visualise is not None:
        ip, port = opts.visualise.split(":")
        vis_client = udp_client.UDPClient(ip, int(port))
        def visualise_callback(message):
            vis_client.send(message)

    server = Server(DEFAULT_SERVER_PORT, client, visualise_callback)
    server.run_forever()

if __name__ == '__main__':
    main()
