import gc
import array
import machine
import time
import network
import socket

from bme280 import BME280
from mpu6050 import MPU
from protocol import Protocol

# SCL = 12
# SDA = 14
SCL = 27
SDA = 26

PORT = 5000

KNOWN_NETWORKS = {
    b'TP-LINK_2.4GHz_BBADE9': b'51790684',
}

def setup_i2c():
    scl = machine.Pin(SCL, machine.Pin.OUT)
    sda = machine.Pin(SDA, machine.Pin.OUT)
    i2c = machine.I2C(freq=400000, scl=scl, sda=sda)
    return i2c


def setup_bmp280(i2c):
    pressure_sensor = BME280(i2c=i2c)
    return pressure_sensor


def setup_mpu(i2c):
    return MPU(i2c)


def ip2bits(ip):
    res = 0
    for part in ip.split("."):
        res <<= 8
        res |= int(part)
    return res


def bits2ip(bits):
    res = []
    for i in range(4):
        res.append(str(bits & 0xff))
        bits >>= 8
    return ".".join(reversed(res))


def setup_wifi():
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    networks = nic.scan()
    broadcast_address = None
    for name, *_ in networks:
        if name in KNOWN_NETWORKS:
            nic.connect(name, KNOWN_NETWORKS[name])
            print("Connected to {}".format(name.decode("ascii")))
            ip, netmask, _, _ = nic.ifconfig()
            bca_bits = ip2bits(ip)
            netmask_bits = ip2bits(netmask)
            bca_bits &= netmask_bits
            bca_bits |= ~netmask_bits
            broadcast_address = bits2ip(bca_bits)
    return nic, broadcast_address


def setup_socket(nic):
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )
    while not nic.isconnected():
        time.sleep(.1)
    sock.settimeout(2.0)
    ip, *_ = nic.ifconfig()
    sock.bind((ip, PORT))
    return sock


def setup_all():
    i2c = setup_i2c()
    pressure_sensor = setup_bmp280(i2c)
    mpu = setup_mpu(i2c)
    return pressure_sensor, mpu


def main(name="BOB\0"):
    pressure_sensor, mpu = setup_all()
    nic, broadcast_address = setup_wifi()
    s = setup_socket(nic)
    protocol = Protocol(name)
    bmp_data = array.array("i", [0, 0, 0])
    address = (broadcast_address, PORT)
    protocol_buffer = protocol.buffer
    then = time.time()
    while True:
        # pressure_sensor.read_compensated_data(bmp_data)
        # protocol.message(bmp_data[0], bmp_data[1])
        s.sendto(protocol_buffer, address)
        if time.time() - then > 1:
            print(gc.mem_free())
            gc.collect()
            then += 1
