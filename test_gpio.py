from gpiozero import InputDevice, Button
from time import sleep

sensor1 = InputDevice(21, pull_up=False)

while True:
    print(sensor1.value)
    sleep(0.2)