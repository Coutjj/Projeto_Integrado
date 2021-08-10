from gpiozero import InputDevice, Button
from time import sleep

sensor1 = InputDevice(21, pull_up=False)
sensor2 = InputDevice(20, pull_up=False)
sensor3 = InputDevice(16, pull_up=False)

while True:
    if sensor1.is_active:
        print('Sensor 1 acionado')
    if sensor2.is_active:
        print('Sensor 2 acionado')
    if sensor3.is_active:
        print('Sensor 3 acionado')


    sleep(0.5)