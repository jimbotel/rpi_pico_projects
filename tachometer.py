# import the require libraries
#from machine import Pin
import machine
import utime

# global variable
counter = 0

# constants
SAMPLING_TIME = 2 # ( in seconds )
                  # You may also ask the user to input sample time

# pin declaration
tachometerPin = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
#tachometerPin = Pin(15, Pin.IN, Pin.PULL_DOWN)
fan1_pwm = machine.PWM(machine.Pin(4))
fan1_pwm.freq(25000)
percent = 0
fan1_pwm.duty_u16(int(percent*65535/100))

# interrupt handler function
def tachometer(pin):# pin is default positional argument
    global counter
    counter += 1
    
# attach the interrupt to the tachometer Pin
#tachometerPin.irq(trigger = Pin.IRQ_RISING, handler = tachometer)
tachometerPin.irq(trigger = machine.Pin.IRQ_FALLING, handler = tachometer)

# main logic/ function of the program
while True:
    print("Duty_Cycle     Avg_RPMs")
    for percent in range(0,110,10):
        #print("Duty Cycle:", percent)
        fan1_pwm.duty_u16(int(percent*65535/100))
        utime.sleep(2)
        avgrpm = 0
        for t in range(0,10):
            counter = 0
            utime.sleep(SAMPLING_TIME)
            revolutions_per_minute = 60 * counter / (2 * SAMPLING_TIME)
            avgrpm += revolutions_per_minute
            #print("counter:",counter,"RPM:", revolutions_per_minute)
        #print("Duty_Cycle:",percent, "Avg_RPMs:",avgrpm/10)
        print("{}  {:4.0f}".format(percent, avgrpm/10))
    break
#    revolutions_per_minute = 60 * counter / (2 * SAMPLING_TIME)
#    print("tachometer value =", tachometerPin.value())
#    print("counter =",counter)
#    print("RPM : ", revolutions_per_minute )
    # reset the counter to zero 
#    counter = 0
percent = 50
fan1_pwm.duty_u16(int(percent*65535/100))
