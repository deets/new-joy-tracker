import machine

from bme280 import BME280

SCL = 12
SDA = 14

def setup_i2c():
    scl = machine.Pin(SCL, machine.Pin.OUT)
    sda = machine.Pin(SDA, machine.Pin.OUT)
    i2c = machine.I2C(freq=400000, scl=scl, sda=sda)
    return i2c


def setup_bmp280(i2c):
    pressure_sensor = BME280(i2c=i2c)
    return pressure_sensor


def setup_all():
    i2c = setup_i2c()
    pressure_sensor = setup_bmp280(i2c)
    return pressure_sensor
