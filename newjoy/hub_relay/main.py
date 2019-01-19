# -*- mode: python -*-
import time
import logging

import serial
from pythonosc import osc_message_builder
from pythonosc import udp_client

from ..common import (
    core_argument_parser,
    core_app_setup,
    DEFAULT_SERIAL_PORT,
    DEFAULT_BAUD,
)

from .parser import BaseProtocolParser, PackageParser
from .stats import Statistics

logger = logging.getLogger(__name__)


def parse_args():
    parser = core_argument_parser()
    parser.add_argument("--baud", default=DEFAULT_BAUD, type=int)
    parser.add_argument("--port", default=DEFAULT_SERIAL_PORT)
    parser.add_argument("--osc-port", default=10000)
    parser.add_argument("--osc-host", default="localhost")
    opts = parser.parse_args()
    core_app_setup(opts)
    return opts


def send_osc_message(client, name, descriptor, payload):
    b = osc_message_builder.OscMessageBuilder("/{}".format(name))
    b.add_arg("".join(k for k, _ in descriptor))
    for v in payload:
        b.add_arg(v)
    client.send(b.build())


def send_visualisation_message(vis_client, name, packet_diff):
    b = osc_message_builder.OscMessageBuilder("/{}".format(name))
    b.add_arg(time.monotonic())
    b.add_arg(packet_diff)
    vis_client.send(b.build())


def main():
    opts = parse_args()
    p = serial.Serial(
        opts.port,
        opts.baud,
    )
    parser = BaseProtocolParser()
    package_parser = PackageParser()
    stats = Statistics()
    message_count = 0
    client = udp_client.UDPClient(opts.osc_host, opts.osc_port)
    vis_client = udp_client.UDPClient(opts.osc_host, 11111)
    while True:
        count = p.inWaiting()
        if count:
            data = p.read(count)
            for message in parser.feed(data):
                message_type, data = package_parser.feed(message)
                if message_type == "S":
                    name, descriptor, payload, packet_diff = data
                    stats.feed(name, packet_diff)
                    send_osc_message(client, name, descriptor, payload)
                    send_visualisation_message(vis_client, name, packet_diff)
                elif message_type == "H":
                    logger.info("HUB status data: %r", data)
                    logger.info("Serial package stats: %s", str(stats))
                    logger.info(
                        "messages: {} bytes: {} message-chars: {} lost-chars: {} loss-rate {:2.1f} buffer-length: {}".format(
                            message_count, parser.total_chars, parser.message_chars,parser.lost_chars, (parser.lost_chars / parser.total_chars) * 100, len(parser)
                        )
                    )

if __name__ == '__main__':
    main()
