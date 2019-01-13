# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import struct
import logging

from .naming import resolve

logger = logging.getLogger(__name__)

TASKS = {
    1: "MPU6050",
    2: "BMP280",
}

TASK_CONFIG = {
    "MPU6050": "fffffff",
    "BMP280": "I",
}


class PackageParser:

    def __init__(self, resolve=resolve):
        self.invalid_count = 0
        self._resolve = resolve
        self._parsers = {}

    def feed(self, data):
        # increase until we know it's correct
        self.invalid_count += 1
        if data[0] != ord('#'):
            logger.debug("malformed data, no leading #")
            return
        if len(data) < 3:
            logger.debug("malformed data, too short")

        length = data[1]
        length_inv = data[2]
        if length != length_inv ^ 0xff:
            logger.debug("malformed data, length field inconsistent")
            return []

        if len(data) != length:
            logger.debug("malformed data, length field and length of data mismatch")
        id_ = data[3:3 + 6]
        name = self._resolve(id_)
        if name not in self._parsers:
            self._parsers[name] = self._setup_parser(data, name)
        return [(name, self._parsers[name](data))]

    def _setup_parser(self, data, name):
        start = 1 + 2 + 6  # start marker (#), length, esp32 id
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

        for i in range(task_num):
            kind = descriptor[i // 2]
            kind >>= 4 * (i % 2)
            kind &= 0xf
            task_type = TASKS[kind]
            logger.info("%i task is %s", i + 1, task_type)
            task_format = TASK_CONFIG[task_type]
            payload_length += struct.calcsize(task_format)
            format += task_format

        logger.info("%s payload_length: %i", name, payload_length)
        format = "<{}".format(format)
        return lambda data: struct.unpack(format, data[payload_start:payload_start + payload_length])
