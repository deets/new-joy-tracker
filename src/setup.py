import machine
import time
import socket
import mpu6050

import ustruct

from wifi import setup_wifi
import bme280

I2C_BUSSES = [
    (27, 26),
    (17, 16),
    (4, 0)
]

CLK = 18  # SPI bus for 24L01
MOSI = 23
MISO = 22
CS0 = 5
CE = 19  # chip enable for 24L01
IRQ = 21

PORT = 5000
CONNECT_TIMEOUT = 100
RESET_COUNT = 10  # after these, we try to reset the board for reconnection
LOOP_SLEEP_MS = 70
SENSOR_PERIOD = 2  # in milliseconds
I2C_FREQUENCY = 1000_000

BMP280S = []
MPU6050S = []


def setup_i2c_busses():
    for scl, sda in I2C_BUSSES:
        scl = machine.Pin(scl, machine.Pin.OUT)
        sda = machine.Pin(sda, machine.Pin.OUT)
        yield machine.I2C(freq=I2C_FREQUENCY, scl=scl, sda=sda)


def setup_socket(nic):
    while not nic.isconnected():
        time.sleep(.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock


def setup_all():
    for i2c in setup_i2c_busses():
        print("scanning bus", i2c)
        if mpu6050.present_on_bus(i2c):
            MPU6050S.append(
                mpu6050.MPU(
                    i2c=i2c,
                    address=mpu6050.present_on_bus(i2c)
                )
            )

        if bme280.present_on_bus(i2c):
            BMP280S.append(
                bme280.BME280(
                    i2c=i2c,
                    address=bme280.present_on_bus(i2c)
                )
            )



def main():
    while True:
        try:
            setup_all()
            for _ in range(10):
                for bmp in BMP280S:
                    print(bmp.values)
                for mpu in MPU6050S:
                    print(mpu.read_sensors_scaled())
                time.sleep(.2)
        except OSError:
            pass

    while True:
        try:
            nic, destination_address = setup_wifi()
            break
        except Exception:
            pass

    reconnect_count = 0
    while True:
        print("connecting...")
        try:
            s = setup_socket(nic)
            while True:
                #protocol.update()
                for bmp in BMP280S:
                    print(bmp.values)

                print(ustruct.unpack_from("ffff", protocol.buffer, 12))
                s.sendto(protocol.buffer, (destination_address, PORT))
                time.sleep_ms(LOOP_SLEEP_MS)
                machine.idle()
        except OSError:
            reconnect_count += 1
            if reconnect_count > RESET_COUNT:
                print("resetting hard")
                machine.reset()
            time.sleep(1)
