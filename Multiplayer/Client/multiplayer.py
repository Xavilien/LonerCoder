import random
from time import time
import threading
from tfimgcontroller import FaceDetection
import sys
import math

from Server.multiplayer_client_test import Client

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
    Builder.load_file('Client/multiplayer.kv')
except FileNotFoundError:
    pass


class PongPaddle(Widget):
    pass


class PongBall(Widget):
    pass


class PongGame(ScreenManager):
    ball = ObjectProperty(None)
    top_player = ObjectProperty(None)
    bottom_player = ObjectProperty(None)
    detector = None

    # Allow us to close thread before exiting the app
    control = threading.Event()
    control.set()

    def __init__(self):
        super(PongGame, self).__init__()

        self.current = 'play'
        self.player = None
        self.opponent = None
        self.client = None

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

        self.client = Client(self.top_player.center_x)
        self.client.s.sendall(str(self.x).encode('utf-8'))
        player = self.client.s.recv(4096).decode("utf8")
        print(player)

        if player == "top_player":
            self.player = self.top_player
            self.opponent = self.bottom_player
        elif player == "bottom_player":
            self.player = self.bottom_player
            self.opponent = self.top_player
        else:
            raise Exception("player not assigned")

        self.client.start()

        while not len(self.client.data):
            pass

        if self.control.is_set():
            self.ball.opacity = 1
            self.ids.start.text = 'Starting'
            Clock.schedule_once(self.start, 1)

    def start(self, dt):
        self.ids.start.text = ''
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def reset(self):
        self.player.center_x = self.width/2

    def player_movement(self):
        # Update position of head by adding the offset to half the width
        sensitivity = 2
        offset = (0.5 - self.detector.x) * self.width  # How far the head is from the center
        playerpos = self.width / 2 + offset * sensitivity

        center = self.player.center_x
        width = self.ids.player_bottom.size[0]/2

        if abs(center - playerpos) < width:
            return None
        elif playerpos > center and center < self.width - width:
            self.player.center_x += dp(20)
        elif playerpos < center and center > width:
            self.player.center_x -= dp(20)

        self.client.x = self.player.center_x

    def opponent_movement(self):
        self.opponent.center_x = self.client.data[1]

    def ball_movement(self):
        self.ball.center_x = self.client.data[0][0]
        self.ball.center_y = self.client.data[0][1]
        
    def update(self, dt):
        self.player_movement()
        self.opponent_movement()
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
