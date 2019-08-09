#!/usr/bin/env python
# -*- coding: utf-8 -*-

from machine import Pin

from Blinker.Blinker import Blinker, BlinkerButton, BlinkerNumber
from Blinker.BlinkerDebug import *

auth = 'Your Device Secret Key'
ssid = 'Your WiFi network SSID or name'
pswd = 'Your WiFi network WPA password or WEP key'

BLINKER_DEBUG.debugAll()

Blinker.mode('BLINKER_WIFI')
Blinker.begin(auth, ssid, pswd)

def data_callback(data):
    BLINKER_LOG('Blinker readString: ', data)
    text1.print("os time", millis())

Blinker.attachData(data_callback)

if __name__ == '__main__':

    while True:
        Blinker.run()
