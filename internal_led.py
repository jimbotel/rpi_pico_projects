import machine
import utime

led_onboard = machine.Pin('LED', machine.Pin.OUT)

while True:
    led_onboard.on()
    utime.sleep(5)
    led_onboard.off()
    utime.sleep(5)
