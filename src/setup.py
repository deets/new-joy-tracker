import array
import machine
import time
import network
import socket
import struct

from bme280 import BME280, BME280_I2CADDR
from mpu6050 import MPU
from protocol import Protocol

# SCL = 12
# SDA = 14
SCL = 27
SDA = 26

PORT = 5000
CONNECT_TIMEOUT = 100
RESET_COUNT = 10 # after these, we try to reset the board for reconnection

KNOWN_NETWORKS = {
    b'TP-LINK_2.4GHz_BBADE9': (b'51790684', '192.168.2.104'),
}

def setup_i2c():
    scl = machine.Pin(SCL, machine.Pin.OUT)
    sda = machine.Pin(SDA, machine.Pin.OUT)
    i2c = machine.I2C(freq=400000, scl=scl, sda=sda)
    return i2c


def setup_bmp280(i2c):
    if BME280_I2CADDR in i2c.scan():
        pressure_sensor = BME280(i2c=i2c)
    else:
        pressure_sensor = None
        print('no pressure sensor detected')
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
    sock.connect((destination_address, PORT))
    return sock


def setup_all():
    i2c = setup_i2c()
    pressure_sensor = setup_bmp280(i2c)
    mpu = setup_mpu(i2c)
    return pressure_sensor, mpu


def main(name="BOB\0"):
    pressure_sensor, mpu = setup_all()
    nic, destination_address = setup_wifi()
    protocol = Protocol(name)
    reconnect_count = 0
    while True:
        print("connecting...")
        try:
            s = setup_socket(nic, destination_address, )
            while True:
                protocol.read_sensors(pressure_sensor, mpu)
                s.write(protocol.buffer)
                time.sleep_ms(20)
        except OSError:
            reconnect_count += 1
            if reconnect_count > RESET_COUNT:
                print("resetting hard")
                machine.reset()
            time.sleep(1)
