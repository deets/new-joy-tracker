# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import ustruct
import utime
import newjoy
import machine

from names import MAPPING, get_name

SENSOR_MESSAGE = ord(b'S')
HUB_STATUS_MESSAGE = ord(b'H')


def compute_crc(buffer):
    crc = 0
    for b in buffer[3:-1]:
        crc += b
        crc &= 0xff
    buffer[-1] = crc


class Protocol:

    TASK_SPEC = {
        newjoy.TASK_MPU6050: "fffffff",
        newjoy.TASK_BMP280: "I",
    }

    TASK_ID = {
        newjoy.TASK_MPU6050: "i",
        newjoy.TASK_BMP280: "p",
    }

    def __init__(self):
        self._tasks = []
        self.buffer = None
        self.payload = None
        self._osc_spec = ""
        self._osc_payload_start = -1
        uid = machine.unique_id()
        if uid in MAPPING:
            self._osc_path = "/" + MAPPING[uid]
        else:
            self._osc_path = "/" + "".join(
                [hex(c)[2:] for c in uid]
            )
        self._osc_descriptor = {
            0: "",
            1: "",
            2: "",
            3: "",
        }

    def register_task(self, bus, address, task, buffer_size, busno):
        self._tasks.append((bus, address, task, buffer_size, busno))

    def assemble(self, sensor_period):
        name = bytearray(get_name()) + b"\0\0"
        assert len(name) == 6
        task_num = len(self._tasks)
        # we have a start-character, '#'
        start_char = 1
        # after that start character, we follow up with the length of the
        # total message.  It's the length in one byte, followd by the
        # XOR of that length.  The reason for this verified storage is
        # that we need a reliable way of syncing after the start-char
        # to the expected number of bytes
        message_length = 2
        # Then comes the unique ID of the device, 6 bytes
        name_length = len(name)
        # Then the message type. This is constant 1 for sensor messages
        type_length = 1
        # After that, the task count and descriptor. The descriptor specifies
        # the attached sensors/tasks, that all have a specific byte-size.
        # Each sensor is described as a nibble, with the first in the lowest
        # nibble of the first byte, second upper nibble, etc.
        task_count = 1
        descriptor_length = task_num // 2 + task_num % 2
        # it follows the payload, the size is the accumulated size of
        # all tasks' storage needs
        payload_size = sum(
            buffer_size for _, _, _, buffer_size, _
            in self._tasks
        )
        # the final checksum is just all bytes so far summed up as uint8_t
        checksum_size = 1
        buffer_size = start_char + message_length + name_length + \
            type_length + task_count + descriptor_length + \
            payload_size + checksum_size

        name_start = start_char + message_length
        type_start = name_start + name_length
        descriptor_byte_count_offset = type_start + type_length
        descriptor_start = descriptor_byte_count_offset + task_count
        original_payload_start = payload_start = descriptor_start + descriptor_length
        padding = 0
        if payload_start % 4:
            padding = 4 - (payload_start % 4)
            payload_start += padding
            buffer_size += padding
            print("added {} padding".format(padding))
        self.payload_start = payload_start
        self.buffer = bytearray(buffer_size)
        self.buffer[0] = ord(b'#')
        self.buffer[1] = buffer_size
        self.buffer[2] = 0xff ^ buffer_size
        self.buffer[name_start:name_start + name_length] = name
        self.buffer[type_start] = SENSOR_MESSAGE
        self.buffer[descriptor_byte_count_offset] = task_num

        for i in range(padding):
            self.buffer[original_payload_start + i] = ord(b'P')

        descriptor = memoryview(self.buffer)[
            descriptor_start:descriptor_start+descriptor_length
        ]
        newjoy.init(sensor_period, self.buffer)
        self._osc_payload_start = task_byte_offset = payload_start

        for i, (bus, address, task, task_size, busno) in enumerate(self._tasks):
            self._osc_spec += self.TASK_SPEC[task]
            self._osc_descriptor[busno] += self.TASK_ID[task]
            offset = i // 2
            current = descriptor[offset]
            current |= task << (4 * (i % 2))
            descriptor[offset] = current
            try:
                newjoy.add_task(bus, address, task, task_byte_offset)
            except ValueError:
                print((bus, address, task, task_byte_offset))
                raise
            task_byte_offset += task_size

        osc_descriptor = ""
        for busno, devices in sorted(self._osc_descriptor.items()):
            if devices:
                osc_descriptor += "{}{}".format(busno, devices)
        self._osc_descriptor = osc_descriptor
        print(self.buffer)
        utime.sleep_ms(100)

    def update(self):
        newjoy.sync()
        compute_crc(self.buffer)
        # print(self.buffer)
        return bytearray(self.buffer)

    def send_osc(self, osc):
        args = ustruct.unpack_from(
            self._osc_spec,
            self.buffer,
            self._osc_payload_start,
        )
        osc.send(self._osc_path, *((self._osc_descriptor,) + args))


def assemble_hub_status_message(max_deltas, buffer=None):
    # header, length, name, type,
    total_length = 1 + 2 + 6 + 1 + ((4 + 4) * len(max_deltas)) + 1
    print("total_length", total_length)
    if buffer is None or len(buffer) != total_length:
        buffer = bytearray(total_length)
    buffer[0] = ord(b'#')
    buffer[1] = total_length
    buffer[2] = 0xff ^ total_length
    offset = 3
    name = bytearray(get_name()) + b"\0\0"
    buffer[offset:offset + len(name)] = name
    offset += len(name)
    buffer[offset] = HUB_STATUS_MESSAGE
    offset += 1
    for spoke_name, max_delta in max_deltas.items():
        buffer[offset:offset+4] = bytearray(spoke_name)
        offset += 4
        buffer[offset:offset+4] = ustruct.pack('I', max_delta)
        offset += 4

    compute_crc(buffer)
    return buffer
