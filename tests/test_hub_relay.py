# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import logging
import unittest
import pathlib

from newjoy.hub_relay.parser import BaseProtocolParser, PackageParser

logger = logging.getLogger(__name__)


with (pathlib.Path(__file__).parent / "hub-data").open("rb") as inf:
    DATA = inf.read()


NAMES = {
    b'\xb4\xe6-\xbf\xda\xb5': "OTTO",
}


def resolve(id_):
    return NAMES[id_]


class ParserTests(unittest.TestCase):

    def test_full(self):
        parser = BaseProtocolParser()
        messages = list(parser.feed(DATA))
        self.assertGreater(len(messages), 10)
        print(
            "messages:", len(messages),
            "bytes:", parser.total_chars,
            "message-chars:", parser.message_chars,
            "buffer-length:", len(parser)
        )

    def test_byte_by_byte(self):
        parser = BaseProtocolParser()
        all_messages_in_one_go = list(parser.feed(DATA))

        messages = []
        parser = BaseProtocolParser()
        for c in DATA:
            messages.extend(list(parser.feed(bytes([c]))))

        self.assertEqual(
            all_messages_in_one_go,
            messages,
        )

    def test_package_parsing(self):
        package = b'#m\x92IRIS\x00\x00S\x05\x11"\x01PP]\x89\x7f?\xdfxH\xbb\x1f\xe9\xb39\xa3h{<\x00\x00X\xbb\x00\x00\x14\xbc\x00\x10\x81?\xc2\x83\x7f?\xdc`\x97:\xa8\xef\xe9\xba\xb5\x13\xa6\xbc\x00\x00`;\x00\x00\x08;\x00\xd8\x7f?;J\x00\x00\'Q\x00\x00\x93&\x7f?\x1c\xb9\xf8\xb9|p\xa49\x1e\x91i=\x00\x00\xac\xbb\x00\x00\x00\x00\x00X\x82?\x8c'
        package_parser = PackageParser()
        kind, (name, descriptor, imu, packet_diff) = package_parser.feed(package)


    def test_all_package_parsing(self):
        package_parser = PackageParser()
        parser = BaseProtocolParser()
        for message in parser.feed(DATA):
            message_type, data = \
                package_parser.feed(message)
            if message_type == "S":
                (name, descriptor, payload, packet_diff) = data
                #print(payload)
            elif message_type == "H":
                print(data)

    def test_hub_status_package_parsing(self):
        data = b'#\x13\xecOTTO\x00\x00HIRIS\x00\x00\x0e\x00\xd3'
        package_parser = PackageParser()
        kind, data = package_parser.feed(data)
        self.assertEqual(kind, "H")
        print(data)
