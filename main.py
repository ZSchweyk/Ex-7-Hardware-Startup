import os
import random
from threading import Thread

import spidev
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from Slush.Devices import L6470Registers



os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from pidev.kivy.selfupdatinglabel import SelfUpdatingLabel

from datetime import datetime
import time

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'


# os.environ["DISPLAY"] = ":0"
# pygame.display.init()


class MotorGUI(App):
    def build(self):
        return SCREEN_MANAGER


Window.clearcolor = (0, 0, 0, 0)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file("main.kv")
        super(MainScreen, self).__init__(**kwargs)
        self.m1 = stepper(port=1, micro_steps=32, hold_current=20, run_current=20, accel_current=20,
                          deaccel_current=20,
                          steps_per_unit=200, speed=2)
        self.spi = spidev.SpiDev()

    def turn_motor_on_off(self, text):
        toggle_motor_status_btn = ObjectProperty(None)
        if text == "Turn On":
            self.m1.go_until_press(0, 6400)
            print("On")
            self.toggle_motor_status_btn.text = "Turn Off"
        else:
            self.m1.free_all()
            self.spi.close()
            # GPIO.cleanup()
            print("Off")
            self.toggle_motor_status_btn.text = "Turn On"

    def change_motor_direction(self, dir):
        if self.m1.isBusy():
            motor_direction = ObjectProperty(None)
            self.m1.stop()
            if dir == "CW":
                self.motor_direction.text = "CCW"
                self.m1.go_until_press(0, 6400)
            else:
                self.motor_direction.text = "CW"
                self.m1.go_until_press(1, 6400)


    def stop_motor(self):
        self.m1.stop()
        self.m1.free_all()
        self.spi.close()
        GPIO.cleanup()


Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))

if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    MotorGUI().run()
