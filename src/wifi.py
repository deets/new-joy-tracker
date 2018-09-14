# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import network


KNOWN_NETWORKS = None

def load_known_networks():
    global KNOWN_NETWORKS
    if KNOWN_NETWORKS is None:
        KNOWN_NETWORKS = []
        with open("networks.txt", "rb") as inf:
            for line in inf:
                line = line.strip()
                if line:
                    ssid, password, dest = line.split(b":")
                    KNOWN_NETWORKS.append((ssid, password, dest))
    return KNOWN_NETWORKS


def setup_wifi():
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    networks = nic.scan()
    for name, *_ in networks:
        for ssid, password, destination_address in KNOWN_NETWORKS:
            if ssid == name:
                nic.connect(name, password)
                print("Connected to {}".format(name.decode("ascii")))
                return nic, destination_address
    raise Exception("Couldn't connect to WIFI network!")

load_known_networks()
