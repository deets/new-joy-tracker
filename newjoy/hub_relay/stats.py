# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import pprint


class Statistics:

    def __init__(self):
        self._packet_diff_maxs = {}

    def feed(self, name, packet_diff):
        self._packet_diff_maxs[name] = max(
            packet_diff,
            self._packet_diff_maxs.get(name, 0),
        )

    def __str__(self):
        return pprint.pformat(self._packet_diff_maxs)
