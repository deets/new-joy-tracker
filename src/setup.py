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
CONNECT_TIMEOUT = 100

KNOWN_NETWORKS = {
    b'TP-LINK_2.4GHz_BBADE9': (b'51790684', '192.168.2.104'),
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
            password, destination_address = KNOWN_NETWORKS[name]
            nic.connect(name, password)
            print("Connected to {}".format(name.decode("ascii")))
            break
    else:
        raise Exception("Couldn't connect to WIFI network!")
    return nic, destination_address


def setup_socket(nic, destination_address):
    while not nic.isconnected():
        time.sleep(.1)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    for _ in range(CONNECT_TIMEOUT):
        try:
            sock.connect((destination_address, PORT))
        except OSError as e:
            sock.close()
            time.sleep(1)
            print("socket connect failed, retry")
        else:
            break
    return sock


def setup_all():
    i2c = setup_i2c()
    #pressure_sensor = setup_bmp280(i2c)
    mpu = setup_mpu(i2c)
    return None, mpu


def main(name="BOB\0"):
    pressure_sensor, mpu = setup_all()
    nic, destination_address = setup_wifi()
    s = setup_socket(nic, destination_address, )
    bmp_data = array.array("i", [0, 0, 0])

    protocol = Protocol(name)
    bmp_data = array.array("i", [0, 0, 0])
    address = (broadcast_address, PORT)
    protocol_buffer = protocol.buffer
    while True:
        #pressure_sensor.read_compensated_data(bmp_data)
        mpu.read_sensors()
        s.write(mpu.sensors)
