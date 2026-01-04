# MicroPython main.py - simple sensor reporting to Aurora Core via WiFi
import network, time, urequests, json, machine

SSID = "yourssid"
PSK = "yourpass"
AURORA_HOST = "192.168.1.100"
AURORA_PORT = 9701

def connect():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(SSID, PSK)
    for _ in range(20):
        if sta.isconnected():
            print("connected")
            return True
        time.sleep(1)
    return False

def report():
    data = {"temp": 42}
    try:
        urequests.post("http://%s:%d/api/edge/telemetry" % (AURORA_HOST,AURORA_PORT), json=data)
    except:
        pass

if connect():
    while True:
        report()
        time.sleep(30)
