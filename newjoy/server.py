#!/usr/bin/env python3.6
import struct
import argparse
import time
import logging

from functools import partial
from socket import socket, SO_REUSEADDR, SOL_SOCKET, SOCK_DGRAM, AF_INET
from asyncio import Task, coroutine, get_event_loop, DatagramProtocol
from math import atan2, asin

from pythonosc import osc_message_builder
from pythonosc import udp_client

from .util import PackageParser
from .naming import resolve
from .logger import Logger

DEFAULT_UDP_PORT = 5005
DEFAULT_SERVER_PORT = 5000
OSC_PATH = "/filter"

logger = logging.getLogger(__name__)

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


def compute_angles(q0, q1, q2, q3):
  roll = atan2(q0*q1 + q2*q3, 0.5 - q1*q1 - q2*q2) *  57.29578
  pitch = asin(-2.0 * (q1*q3 - q0*q2)) * 57.29578
  yaw = atan2(q1*q2 + q0*q3, 0.5 - q2*q2 - q3*q3) * 57.29578 + 180.0
  return roll, pitch, yaw


def message_processor(client, visualise_callback, logging_callback):
    parser = PackageParser(resolve)
    last_timestamps = {}

    while True:
        message = yield
        name, data = parser.feed(message)
        print(name, data)
        # b = osc_message_builder.OscMessageBuilder(OSC_PATH)
        # b.add_arg(name)
        # b.add_arg(pressure)
        # b.add_arg(g_x)
        # b.add_arg(g_y)
        # b.add_arg(g_z)
        # b.add_arg(acc_x)
        # b.add_arg(acc_y)
        # b.add_arg(acc_z)
        # b.add_arg(packet_diff)

        # message = b.build()
        # client.send(message)
        # visualise_callback(message)
        # logging_callback(message)


class NewJoyProtocol(DatagramProtocol):

    def __init__(self, server, *a, **k):
        super().__init__(*a, **k)
        self._server = server
        self._transport = None
        self._ip2name_mapping = {}


    def connection_made(self, transport):
        self._transport = transport


    def datagram_received(self, data, addr):
        logger.debug(data)
        self._server._message_processor.send(data)


class Server(object):
    def __init__(self, port, client, visualise_callback, logging_callback):
        self._loop = get_event_loop()
        self._message_processor = message_processor(
            client,
            visualise_callback,
            logging_callback,
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
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-l", "--log")
    opts = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if opts.debug else logging.INFO,
    )

    client = udp_client.UDPClient(opts.destination, opts.port)

    def logging_callback(*_):
        pass

    def visualise_callback(_):
        pass

    if opts.log:
        logging_callback = Logger(opts.log).logging_callback

    if opts.visualise is not None:
        ip, port = opts.visualise.split(":")
        vis_client = udp_client.UDPClient(ip, int(port))
        def visualise_callback(message):
            vis_client.send(message)

    server = Server(DEFAULT_SERVER_PORT, client, visualise_callback, logging_callback)
    server.run_forever()

if __name__ == '__main__':
    main()
