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
                          steps_per_unit=200, speed=8)
        self.spi = spidev.SpiDev()
        self.m_dir = 0
        speed_value = ObjectProperty(None)
        self.motor_speed = lambda speed: 80 * speed / 100 * self.m1.speed
        self.motor_status = False

    def is_motor_on(self):
        """
        Motor is considered on if its not closed (self.spi.close()), regardless of its speed (can be zero).

        Had to make this method because self.m1.isBusy() tests if the motor is moving, rather than if its not closed.

        :return: True or False
        """
        return self.motor_status and self.m1.speed >= 0

    def move_motor(self):
        self.m1.go_until_press(self.m_dir, int(self.motor_speed(self.speed_value.value)))

    def turn_motor_on_off(self, text):
        toggle_motor_status_btn = ObjectProperty(None)
        if text == "Turn On":
            self.move_motor()
            self.toggle_motor_status_btn.text = "Turn Off"
            self.motor_status = True
        else:
            self.m1.free_all()
            self.spi.close()
            self.toggle_motor_status_btn.text = "Turn On"
            self.motor_status = False

    def change_motor_direction(self):
        if self.is_motor_on():
            motor_direction = ObjectProperty(None)
            self.m1.stop()
            if self.m_dir == 1:
                self.motor_direction.text = "CCW"
                self.m_dir = 0
            else:
                self.motor_direction.text = "CW"
                self.m_dir = 1
            self.move_motor()

    def change_speed(self):
        # m.set_speed(.5)
        # m.relative_move(10)
        if self.is_motor_on():
            self.m1.stop()
            self.move_motor()

    def run_sequence(self):
        sequence_btn = ObjectProperty(None)
        position_txt = ObjectProperty(None)
        self.m1.stop()
        self.position_txt.text = str(self.m1.get_position_in_units())
        self.m1.set_speed(1)
        self.m1.relative_move(15)
        self.position_txt.text = str(self.m1.get_position_in_units())
        time.sleep(10)
        self.m1.set_speed(5)
        self.m1.relative_move(10)
        self.position_txt.text = str(self.m1.get_position_in_units())
        time.sleep(8)
        self.m1.goHome()
        time.sleep(30)
        self.position_txt.text = str(self.m1.get_position_in_units())
        self.m1.set_speed(8)
        self.m1.relative_move(-100)
        self.position_txt.text = str(self.m1.get_position_in_units())
        time.sleep(10)
        self.m1.goHome()
        self.position_txt.text = str(self.m1.get_position_in_units())
        return

    def close_motor(self):
        self.m1.stop()
        self.m1.free_all()
        self.spi.close()
        GPIO.cleanup()

    def exit_program(self):
        self.close_motor()
        quit()


Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))

if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    MotorGUI().run()
