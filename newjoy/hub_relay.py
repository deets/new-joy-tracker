# -*- mode: python -*-
import serial
import logging
import struct
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client


from .common import (
    core_argument_parser,
    core_app_setup,
    DEFAULT_SERIAL_PORT,
    DEFAULT_BAUD,
)
from .naming import resolve

logger = logging.getLogger(__name__)


class PackageParser:

    TASKS = {
        1: "MPU6050",
        2: "BMP280",
    }
    OSC_DESCRIPTORS = {
        1: ("i", 7),
        2: ("p", 1)
    }

    TASK_CONFIG = {
        "MPU6050": "fffffff",
        "BMP280": "I",
    }

    def __init__(self, resolve=resolve):
        self._resolve = resolve
        self._parsers = {}
        self._descriptors = {}
        self._last_message = {}

    def feed(self, package):
        now = time.monotonic()
        id_ = package[3:3 + 6]
        name = id_[:-2]

        if name not in self._parsers:
            self._parsers[name], self._descriptors[name] = self._setup_parser(
                package,
                name,
            )
            self._last_message[name] = now

        packet_diff = now - self._last_message[name]
        self._last_message[name] = now
        return (
            name,
            self._descriptors[name],
            self._parsers[name](package),
            packet_diff,
        )

    def _setup_parser(self, data, name):
        start = 1 + 2 + 6 + 1  # start marker (#), length, esp32 id, type_flag
        task_num = data[start]
        descriptor_length = task_num // 2 + task_num % 2
        payload_start = start + 1 + descriptor_length

        if payload_start % 4:
            padding = 4 - (payload_start % 4)
            payload_start += padding

        logger.info("%s has %i tasks configured, payload_start: %i", name, task_num, payload_start)
        descriptor = data[start + 1:payload_start]
        format = ""
        payload_length = 0

        osc_descriptor = []

        for i in range(task_num):
            kind = descriptor[i // 2]
            kind >>= 4 * (i % 2)
            kind &= 0xf
            task_type = self.TASKS[kind]
            osc_descriptor.append(self.OSC_DESCRIPTORS[kind])
            logger.info("%i task is %s", i + 1, task_type)
            task_format = self.TASK_CONFIG[task_type]
            payload_length += struct.calcsize(task_format)
            format += task_format

        logger.info("%s payload_length: %i", name, payload_length)
        format = "<{}".format(format)
        return (
            lambda data: struct.unpack(
                format,
                data[payload_start:payload_start + payload_length]
            ),
            osc_descriptor,
        )


class BaseProtocolParser:

    def __init__(self):
        self._buffer = b''
        self.total_chars = 0
        self.message_chars = 0

    def feed(self, data):
        self._buffer += data
        self.total_chars += len(data)

        searchpos = 0

        while searchpos < len(self._buffer):
            pos = self._buffer.find(b"#", searchpos)
            if pos == -1:
                break
            try:
                length = self._buffer[pos + 1]
                xor_length = self._buffer[pos + 2]
            except IndexError:
                # we reached the end of the buffer
                break

            if length != xor_length ^ 0xff:
                logging.debug("Not a valid header, skipping")
                searchpos += 1
                continue
            candidate = self._buffer[pos:pos + length]
            # if we would reach beyond the length of our
            # current data, we don't really have a candidate
            # and thus stop processing
            if len(candidate) != length:
                break
            crc = sum(b for b in candidate[3:-1]) & 0xff
            if crc == candidate[-1]:
                yield candidate
                self.message_chars += len(candidate)
                searchpos += (pos - searchpos) + length
            else:
                logging.debug("Not a valid CRC, skipping")
                searchpos += 1

        if searchpos != -1:
            self._buffer = self._buffer[searchpos:]

    def __len__(self):
        return len(self._buffer)

    @property
    def lost_chars(self):
        return self.total_chars - self.message_chars


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
    message_count = 0
    client = udp_client.UDPClient(opts.osc_host, opts.osc_port)
    vis_client = udp_client.UDPClient(opts.osc_host, 11111)
    while True:
        count = p.inWaiting()
        if count:
            data = p.read(count)
            for message in parser.feed(data):
                name, descriptor, payload, packet_diff = package_parser.feed(message)
                send_osc_message(client, name, descriptor, payload)
                send_visualisation_message(vis_client, name, packet_diff)

            logger.debug(
                "messages: {} bytes: {} message-chars: {} lost-chars: {} loss-rate {:2.1f} buffer-length: {}".format(
                    message_count, parser.total_chars, parser.message_chars,parser.lost_chars, (parser.lost_chars / parser.total_chars) * 100, len(parser)
                )
            )

if __name__ == '__main__':
    main()
