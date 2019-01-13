# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import logging
import unittest
import pathlib

from newjoy.hub_relay import BaseProtocolParser, PackageParser

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
        messages = parser.feed(DATA)
        self.assertGreater(len(messages), 10)
        print(
            "messages:", len(messages),
            "bytes:", parser.total_chars,
            "message-chars:", parser.message_chars,
            "buffer-length:", len(parser)
        )

    def test_byte_by_byte(self):
        parser = BaseProtocolParser()
        all_messages_in_one_go = parser.feed(DATA)

        messages = []
        parser = BaseProtocolParser()
        for c in DATA:
            messages.extend(parser.feed(bytes([c])))

        self.assertEqual(
            all_messages_in_one_go,
            messages,
        )

    def test_package_parsing(self):
        package = b'#)\xd6\xb4\xe6-\xbf\xda\xb5\x01\x01\x00T\x91\x7f?\x96>;:z\x13\xc7\xb9\x18\xde\xa4\xba\x00\x00`:\x00\x00\xb0:\x00x~?>'
        package_parser = PackageParser()
        name, imu = package_parser.feed(package)
        for a, b in zip(
            (0.9983112812042236, 0.0007142809918150306, -0.0003797074896283448, -0.0012578396126627922, 0.0008544921875, 0.0013427734375, 0.9940185546875),
            imu
        ):
            self.assertAlmostEqual(a, b, places=4)
