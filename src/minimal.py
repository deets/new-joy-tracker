import gc
import array
import machine
import time
import network
import socket

PORT = 5000

KNOWN_NETWORKS = {
    b'TP-LINK_2.4GHz_BBADE9': b'51790684',
}

def ip2bits(ip):
    res = 0
    for part in ip.split("."):
        res <<= 8
        res |= int(part)
    return res


def bits2ip(bits):
    res = []
    for _ in range(4):
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


def main():
    nic, broadcast_address = setup_wifi()
    s = setup_socket(nic)
    address = (broadcast_address, PORT)
    message = "foobar"
    then = time.time()
    count = 0
    print(message, address)

    while True:
        try:
            s.sendto(message, address)

            count += 1
        except OSError:
            print(count)
            raise
        if (count % 1000) == 0:
            print(".")
        # if time.time() - then > 1:
        #     print(gc.mem_free())
        machine.idle()
        time.sleep_ms(20)
        #gc.collect()
        # then += 1
