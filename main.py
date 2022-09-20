# import the require libraries
from machine import Pin, PWM, I2C
from utime import sleep
from dht import DHT22, DHT11
from ssd1306 import SSD1306_I2C
from re import search

NUM_FANS = 4

pwmFanPin = [15, 12, 8, 4]
tachFanPin = [14, 11, 7, 3]
oledfanrow = [20, 30, 40, 50]
pwmFan = []
tachFan =  []

# global variable
counter = [0] * NUM_FANS

# constants
SAMPLING_TIME = 1 # ( in seconds )

# temp to pwm map
xtemp = [ 0, 20, 40, 60, 100]
ypwm  = [30, 30, 60,100, 100]

temp2pwm = [0.0] * 101

if((xtemp[0] != 0) or (xtemp[-1] != 100)):
    print("initial temp must be 0 and end temp must be 100")
    exit(1)

cnt = 0
for i in range( len(xtemp) -1 ):
    if(xtemp[i+1] <= xtemp[i]):
        print("temperatures should always increase in xtemp list")
        exit(1)        
    if(ypwm[i] == ypwm[i+1]):
        pwmInc = 0
    elif(ypwm[i+1] > ypwm[i]):
        pwmInc = (ypwm[i+1]-ypwm[i])/(xtemp[i+1]-xtemp[i])
    else:
        print("Review the definition, pwm duty cycle should not decrease when temperature increases")
        exit(1)
    cnt = xtemp[i]
    temp2pwm[cnt] = ypwm[i]
    cnt += 1
    while(cnt < xtemp[i+1]):
        temp2pwm[cnt] = temp2pwm[cnt-1] + pwmInc
        #print ("temp:",cnt,"pwm:",temp2pwm[cnt])
        cnt += 1
temp2pwm[100] = ypwm[-1]

# print("{0:4} {1}".format("temp","pwm"))
# for itemp,vpwm in enumerate(temp2pwm):
#     print(f'{itemp} {vpwm:.2f}')

# pin declaration
buzzer = Pin(2, Pin.OUT)
buzzer.value(1)
#tempSensor = DHT22(Pin(15))
tempSensor = DHT11(Pin(22))

i2c=I2C(0,sda=Pin(20), scl=Pin(21), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# relay
relay = Pin(28, Pin.OUT)
relay.value(0)

# interrupt handler function
def tachometer(pin):
    global counter
    pn = int(search('Pin\(([0-9]+),',str(pin)).group(1))
    idx = tachFanPin.index(pn)
    counter[idx] += 1

# def tachometer0(pin):
#     global counter
#     counter[0] += 1
# 
# def tachometer1(pin):
#     global counter
#     counter[1] += 1
# 
# def tachometer2(pin):
#     global counter
#     counter[2] += 1
# 
# def tachometer3(pin):
#     global counter
#     counter[3] += 1


# choose starting PWM based on standard "room temperature" (18C)
targetPWM = temp2pwm[18]
# PWM Pins
for i in range(NUM_FANS):
    pwmFan.append( PWM(Pin(pwmFanPin[i])) )
    pwmFan[i].freq(25000)
    pwmFan[i].duty_u16(int(targetPWM*65535/100))

# Tach Pins
for i in range(NUM_FANS):
    tachFan.append(  Pin(tachFanPin[i], Pin.IN, Pin.PULL_UP) )
    tachFan[i].irq(trigger = Pin.IRQ_FALLING, handler = tachometer)
#     if(i == 0):
#         tachFan[i].irq(trigger = Pin.IRQ_FALLING, handler = tachometer0)
#     elif(i == 1):
#         tachFan[i].irq(trigger = Pin.IRQ_FALLING, handler = tachometer1)
#     elif(i == 2):
#         tachFan[i].irq(trigger = Pin.IRQ_FALLING, handler = tachometer2)
#     elif(i == 3):
#         tachFan[i].irq(trigger = Pin.IRQ_FALLING, handler = tachometer3)


#test relay:
relay.value(1)
print("TEST RELAY 5 seconds (NC + rele control HIGH)")
oled.fill(0)
oled.text("TEST RELAY", 0, 32)
oled.text("(5 seconds)", 0, 42)
oled.show()
sleep(5)
relay.value(0)

#test buzzer:
buzzer.value(0)
print("TEST BUZZER")
oled.fill(0)
oled.text("TEST BUZZER", 0, 32)
oled.text("(2 seconds)", 0, 42)
oled.show()
sleep(2)
buzzer.value(1)

rpms = [0] * NUM_FANS

# main logic/ function of the program
while True:
    counter = [0] * NUM_FANS
    sleep(SAMPLING_TIME)
    for i in range(NUM_FANS):
        rpms[i] = 60 * counter[i] / (2 * SAMPLING_TIME)
    tempSensor.measure()
    temp = tempSensor.temperature()
    hum = tempSensor.humidity()
    # int(temp)+1 equivalent to ceil(temp) for positive temp
    targetPWM = temp2pwm[int(temp)+1]

    oled.fill(0)
    oled.text("SPEED: {:.1f}%".format(targetPWM),0,5)
    for i in range(NUM_FANS):
        oled.text("F{}: {:.0f}".format(i+1,rpms[i]), 0, oledfanrow[i])
    oled.text("TEMP:",70, 20)
    oled.text(" {:.1f}C".format(temp), 80, 30)
    oled.text("HUM:", 70, 40)
    oled.text(" {:.1f}%".format(hum), 80, 50)
    oled.show()
    
    print("SPEED (PWM): {:.1f}%".format(targetPWM))
    for i in range(NUM_FANS):
        oled.text("F{}: {:.0f}".format(i+1,rpms[i]), 0, oledfanrow[i])
        print("Fan{}: {:.0f} (counter: {})".format(i+1,rpms[i],counter[i]))
    print("Temperature: {:.1f}C   Humidity: {:.1f}%".format(temp, hum))
    print("---------------------")
    
    for i in range(NUM_FANS):
        pwmFan[i].duty_u16(int(targetPWM*65535/100))
        
    sleep(30)
