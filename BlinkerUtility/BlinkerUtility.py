import time
import network

os_time_start = time.ticks_ms()

def millis():
    return time.ticks_ms() - os_time_start

def macDeviceName():
    wlan = network.WLAN(network.STA_IF)
    s = wlan.config('mac')
    mymac = ('%02x%02x%02x%02x%02x%02x') %(s[0],s[1],s[2],s[3],s[4],s[5])
    return str(mymac).upper()