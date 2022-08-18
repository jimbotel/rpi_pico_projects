# import the require libraries
from machine import Pin, PWM, I2C
from utime import sleep
from dht import DHT22
from ssd1306 import SSD1306_I2C

# global variable
counter = 0

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
buzzer = Pin(22, Pin.OUT)
buzzer.value(1) # 1->OFF , 0->ON
tempSensor = DHT22(Pin(15))
tach1_meter = Pin(2, Pin.IN, Pin.PULL_UP)
fan1_pwm = PWM(Pin(4))
fan1_pwm.freq(25000)

i2c=I2C(1,sda=Pin(26), scl=Pin(27), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# choose starting PWM based on standard "room temperature" (18C)
targetPWM = temp2pwm[18]
fan1_pwm.duty_u16(int(targetPWM*65535/100))
sleep(SAMPLING_TIME)

# interrupt handler function
def tachometer(pin):# pin is default positional argument
    global counter
    counter += 1

# attach the interrupt to the tachometer Pin
tach1_meter.irq(trigger = Pin.IRQ_FALLING, handler = tachometer)

#test buzzer:
buzzer.value(0)
oled.text("TEST BUZZER", 0, 32)
oled.show()
sleep(2)
buzzer.value(1)

# main logic/ function of the program
while True:
    counter = 0
    sleep(SAMPLING_TIME)
    oled.fill(0)
    revolutions_per_minute = 60 * counter / (2 * SAMPLING_TIME)
    print("Duty Cycle (PWM): {:.2f}%".format(targetPWM),"counter:",counter,"RPM:", revolutions_per_minute)
    tempSensor.measure()
    temp = tempSensor.temperature()
    hum = tempSensor.humidity()
    print("Temperature: {}°C   Humidity: {:.0f}% ".format(temp, hum))
    oled.text("Temp: {} C".format(temp), 0, 0)
    oled.text("Humid: {:.0f}% ".format(hum), 0, 16)
    # int(temp)+1 equivalent to ceil(temp) for positive temp
    targetPWM = temp2pwm[int(temp)+1]
    print("New Duty Cycle (PWM): {:.2f}%".format(targetPWM))
    oled.text("Fan load: {:.0f}%".format(targetPWM), 0, 32)
    oled.text("Fan RPM: {:.0f}".format(revolutions_per_minute), 0, 48)
    oled.show()
    fan1_pwm.duty_u16(int(targetPWM*65535/100))
    sleep(30)

