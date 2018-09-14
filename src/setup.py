import array
import machine
import time
import socket
import struct

from bme280 import BME280, BME280_I2CADDR
from mpu6050 import MPU, MPU6050_DEFAULT_ADDRESS
from protocol import Protocol
from wifi import setup_wifi

# SCL = 12
# SDA = 14
# SCL = 27
# SDA = 26
#SCL = 16
#SDA = 17
SCL = 0
SDA = 4

PORT = 5000
CONNECT_TIMEOUT = 100
RESET_COUNT = 10 # after these, we try to reset the board for reconnection
LOOP_SLEEP_MS = 70

def setup_i2c(scl=SCL, sda=SDA):
    scl = machine.Pin(scl, machine.Pin.OUT)
    sda = machine.Pin(sda, machine.Pin.OUT)
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
    try:
        if MPU6050_DEFAULT_ADDRESS in i2c.scan():
            return MPU(i2c)
    except OSError:
        # this can happen because of floating or pulled-up i2cs
        pass
    return None


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


def setup_socket(nic):
    while not nic.isconnected():
        time.sleep(.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock


def setup_all():
    i2c = setup_i2c()
    pressure_sensor = setup_bmp280(i2c)
    mpu = setup_mpu(i2c)
    return pressure_sensor, mpu


def main():
    pressure_sensor, mpu = setup_all()
    while True:
        try:
            nic, destination_address = setup_wifi()
            break
        except Exception:
            pass

    protocol = Protocol()
    reconnect_count = 0
    while True:
        print("connecting...")
        try:
            s = setup_socket(nic)
            while True:
                protocol.read_sensors(pressure_sensor, mpu)
                s.sendto(protocol.buffer, (destination_address, PORT))
                time.sleep_ms(LOOP_SLEEP_MS)
                machine.idle()
        except OSError:
            reconnect_count += 1
            if reconnect_count > RESET_COUNT:
                print("resetting hard")
                machine.reset()
            time.sleep(1)
