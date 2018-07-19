import random
from time import time
import threading
from tfimgcontroller import FaceDetection
import sys

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
    time = Property(0.0)
    highscore = Property(0.0)

    '''
    If the ball has collided with the paddle, the ball changes y direction, as well as x direction based on the offset
    of the ball from the center 
    '''
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_x - self.center_x) / (self.height / 2)
            bounced = Vector(vx, -1 * vy)
            vel = bounced * 1.3
            ball.velocity = vel.x + offset, vel.y


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(ScreenManager):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    detector = None

    jump = dp(20)  # Distance the paddles can move each clock cycle

    start_time = 0  # Allow us to calculate time elapsed since game started

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
        self.serve_ball()
        self.start_time = time()
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    '''
    The ball is not served perpendicular to the paddle so that the player cannot stall by not moving
    '''
    def serve_ball(self, vel=(dp(0.5-random.random()), dp(-5))):
        self.ball.center = self.center
        self.ball.velocity = vel  # Get the ball to start moving

    '''
    Check if the ball has collided with the paddles or the walls
    '''
    def bounce(self):
        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce ball off left or right
        if (self.ball.center_x-25 <= 0) or (self.ball.center_x+25 >= self.width):
            self.ball.velocity_x *= -1  # Change direction so that ball doesn't go off screen

    def check_win(self):
        # went of to a side to end game?
        if self.ball.y < self.y:
            self.reset()
            self.serve_ball()

        # Since it is very unlikely for the player to win, so the game crashes if that happens
        if self.ball.y > self.height:
            self.ids.start.text = 'You beat the game!'
            self.reset()
            self.player1.highscore = '>9000'
            self.player1.time = '>9000'

    '''
    Ensure that the time elapsed will be accurate
    '''
    def reset(self):
        self.start_time = time()
        self.player1.center_x = self.width/2

    '''
    Paddles only move if the x-coordinate of the person is far enough from the center of the paddle so that it is easier
    to keep the paddle still and control it
    
    Paddles move a bit each clock cycle so that the paddles do not seem to 'jump'
    '''
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
        delt = (self.height - self.ball.y) / self.ball.velocity_y
        expected_x = (self.ball.velocity_x * delt) + self.ball.x
        if expected_x > self.width:
            expected_x = self.width
        elif expected_x < self.x:
            expected_x = 0

        center = self.player2.center_x
        width = self.ids.player_top.size[0] / 2

        if abs(center - expected_x) < width:
            return None
        elif center < expected_x:
            self.player2.center_x += self.jump
        elif center > expected_x:
            self.player2.center_x -= self.jump
        
    def update(self, dt):
        self.player1_movement()
        self.player2_movement()
        
        # Update the stopwatch with the time elapsed
        self.player1.time = round(time() - self.start_time, 1)
        try:
            self.player1.highscore = max(self.player1.time, self.player1.highscore)
        except TypeError:
            sys.exit()

        self.ball.move()

        self.bounce()
        self.check_win()


class MultiplayerApp(App):

    def build(self):
        game = PongGame()
        return game

    def on_stop(self):
        self.root.control.clear()
        sys.exit()


if __name__ == '__main__':
    MultiplayerApp().run()
