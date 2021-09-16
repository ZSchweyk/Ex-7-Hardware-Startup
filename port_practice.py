import spidev
import os
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from Slush.Devices import L6470Registers
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus

spi = spidev.SpiDev()

cyprus.initialize()
cyprus.setup_servo(1)

m = stepper(port=1, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
            steps_per_unit=200, speed=8)


motor_speed = lambda speed: 180 * speed / 100 * m.speed


def is_port_on(port):
    check_bin = None
    if port == 6:
        check_bin = 0b0001
    elif port == 7:
        check_bin = 0b0010
    elif port == 8:
        check_bin = 0b0100
    elif port == 9:
        check_bin = 0b1000

    if not cyprus.read_gpio() & check_bin:
        return True
    else:
        return False


def move_motor_if_port_on(port):
    direction = 0
    m.setAccel(0x150)
    m.setDecel(0x100)
    if is_port_on(port):
        m.go_until_press(direction, int(motor_speed(100)))
    else:

        m.softStop()


while True:
    move_motor_if_port_on(6)
    sleep(.1)
