import random
from time import time
import threading
from tfimgcontroller import FaceDetection
import sys
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, Property, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.uix.screenmanager import ScreenManager
from kivy.lang.builder import Builder
from kivy.metrics import dp

from kivy.config import Config
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '800')

# Load the kv file if it is not in the same folder as this file
try:
    Builder.load_file('Multiplayer/multiplayer.kv')
except FileNotFoundError:
    pass


class PongPaddle(Widget):
    pass


class PongBall(Widget):
    pass


class PongGame(ScreenManager):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    detector = None
    angle = 0

    jump = dp(20)  # Distance the paddles can move each clock cycle

    # Allow us to close thread before exiting the app
    control = threading.Event()
    control.set()

    def __init__(self):
        super(PongGame, self).__init__()

        self.current = 'play'

        self.detector = FaceDetection(self.control)
        self.detector.start()

        self.waiting = threading.Thread(target=self.wait)
        self.waiting.start()

    '''
    Wait for the facedetection to be loaded so that the game doesn't start when it is not ready
    '''
    def wait(self):
        while self.detector.x is None and self.control.is_set():
            pass
        if self.control.is_set():
            self.ball.opacity = 1
            self.ids.start.text = 'Starting'
            Clock.schedule_once(self.start, 1)

    def start(self, dt):
        self.ids.start.text = ''
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def reset(self):
        self.player1.center_x = self.width/2

    def player1_movement(self):
        # Update position of head by adding the offset to half the width
        sensitivity = 2
        offset = (0.5 - self.detector.x) * self.width  # How far the head is from the center
        playerpos = self.width / 2 + offset * sensitivity

        center = self.player1.center_x
        width = self.ids.player_bottom.size[0]/2

        if abs(center - playerpos) < width:
            return None
        elif playerpos > center and center < self.width - width:
            self.player1.center_x += self.jump
        elif playerpos < center and center > width:
            self.player1.center_x -= self.jump

    def player2_movement(self):
        pass

    def ball_movement(self):
        pass
        
    def update(self, dt):
        self.player1_movement()
        self.player2_movement()
        self.ball_movement()


class MultiplayerApp(App):

    def build(self):
        game = PongGame()
        return game

    def on_stop(self):
        self.root.control.clear()
        sys.exit()


if __name__ == '__main__':
    MultiplayerApp().run()
