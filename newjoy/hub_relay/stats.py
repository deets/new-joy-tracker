# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import pprint
import time
from collections import defaultdict

class Statistics:

    N = 1000.0

    def __init__(self):
        self._packet_diff_maxs = {}
        self._packet_diff_means = defaultdict(float)
        self._last_ts = {}

    def feed(self, name, packet_diff):
        self._packet_diff_maxs[name] = max(
            packet_diff,
            self._packet_diff_maxs.get(name, 0),
        )
        self._packet_diff_means[name] = \
            self._packet_diff_means[name] + (
                packet_diff - self._packet_diff_means[name]
            ) / self.N

    def timestamp(self, name):
        now = time.monotonic()
        if name in self._last_ts:
            self.feed(name, now - self._last_ts[name])
        self._last_ts[name] = now

    def __str__(self):
        return pprint.pformat(
            {
                "diffs": self._packet_diff_maxs,
                "diff-means": dict(self._packet_diff_means),
            }
        )
