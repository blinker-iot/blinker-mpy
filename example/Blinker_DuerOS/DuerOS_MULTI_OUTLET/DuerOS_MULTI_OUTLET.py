#!/usr/bin/env python
# -*- coding: utf-8 -*-

from machine import Pin

from Blinker.Blinker import Blinker, BlinkerButton, BlinkerNumber, BlinkerDuerOS
from Blinker.BlinkerConfig import *
from Blinker.BlinkerDebug import *

auth = 'Your Device Secret Key'
ssid = 'Your WiFi network SSID or name'
pswd = 'Your WiFi network WPA password or WEP key'

BLINKER_DEBUG.debugAll()

Blinker.mode('BLINKER_WIFI')
Blinker.duerType('BLINKER_DUEROS_MULTI_OUTLET')
Blinker.begin(auth, ssid, pswd)

button1 = BlinkerButton('btn-abc')
number1 = BlinkerNumber('num-abc')

counter = 0
pinValue = 0
wsState = 'on'

p2 = Pin(2, Pin.OUT)
p2.value(pinValue)

def duerPowerState(state, num):
    ''' '''

    BLINKER_LOG("need set outlet: ", num, ", power state: ", state)

    BlinkerDuerOS.powerState(state, num)
    BlinkerDuerOS.print()

def duerQuery(queryCode, num):
    ''' '''

    BLINKER_LOG("DuerOS Query outlet: ", num,", codes: ", queryCode)

    if queryCode == BLINKER_CMD_QUERY_ALL_NUMBER :
        BLINKER_LOG('DuerOS Query All')
        BlinkerDuerOS.powerState(wsState, num)
        BlinkerDuerOS.print()
    elif queryCode == BLINKER_CMD_QUERY_POWERSTATE_NUMBER :
        BlinkerDuerOS.powerState(wsState, num)
        BlinkerDuerOS.print()
    else :
        BlinkerDuerOS.powerState(wsState, num)
        BlinkerDuerOS.print()

def button1_callback(state):
    ''' '''

    BLINKER_LOG('get button state: ', state)

    button1.icon('icon_1')
    button1.color('#FFFFFF')
    button1.text('Your button name or describe')
    button1.print(state)

    global pinValue
    
    pinValue = 1 - pinValue
    p2.value(pinValue)

def data_callback(data):
    global counter
    
    BLINKER_LOG('Blinker readString: ', data)
    counter += 1
    number1.print(counter)

button1.attach(button1_callback)
Blinker.attachData(data_callback)

BlinkerDuerOS.attachPowerState(duerPowerState)
BlinkerDuerOS.attachQuery(duerQuery)

if __name__ == '__main__':

    while True:
        Blinker.run()
