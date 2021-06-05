import random
import threading
import sys

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.uix.screenmanager import ScreenManager
from kivy.lang.builder import Builder
from kivy.metrics import dp

from multiplayer_server_thread import *

from kivy.config import Config

Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '800')

# Load the kv file if it is not in the same folder as this file
try:
    Builder.load_file('Server/server.kv')
except FileNotFoundError:
    pass


class PongPaddle(Widget):
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
    top_player = ObjectProperty(None)
    bottom_player = ObjectProperty(None)

    jump = dp(20)  # Distance the paddles can move each clock cycle

    # Allow us to close thread before exiting the app
    control = threading.Event()
    control.set()

    def __init__(self):
        super(PongGame, self).__init__()

        self.current = 'play'

        self.server = Server(self.control)
        self.server.start()

        self.waiting = threading.Thread(target=self.wait)
        self.waiting.start()

    '''
    Wait for both players to be loaded so that the game doesn't start when it is not ready
    '''

    def wait(self):
        self.server.data["Ball"] = [self.ball.x, self.ball.y]

        while self.server.data["top_player"] is -1 or self.server.data["bottom_player"] is -1:
            pass

        print("Ready")

        if self.control.is_set():
            self.ball.opacity = 1
            self.ids.start.text = 'Starting'
            Clock.schedule_once(self.start, 4)

    def start(self, dt):
        self.ids.start.text = ''
        self.serve_ball()
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    '''
    The ball is not served perpendicular to the paddle so that the player cannot stall by not moving
    '''
    def serve_ball(self, vel=(dp(0.5 - random.random()), dp(-5))):
        self.ball.center = self.center
        self.ball.velocity = vel  # Get the ball to start moving

    '''
    Check if the ball has collided with the paddles or the walls
    '''
    def bounce(self):
        # bounce of paddles
        self.top_player.bounce_ball(self.ball)
        self.bottom_player.bounce_ball(self.ball)

        # bounce ball off left or right
        if (self.ball.center_x - 25 <= 0) or (self.ball.center_x + 25 >= self.width):
            self.ball.velocity_x *= -1  # Change direction so that ball doesn't go off screen

    def check_win(self):
        if self.y < self.ball.y < self.height - 50:  # If the ball is still in play
            return False

        # If the ball goes below the screen, top_player has won
        if self.ball.y <= self.y:
            self.ids.start.text = "Top player has won"
            self.server.winner = "top_player"
            self.ids.top_score.text = str(int(self.ids.top_score.text)+1)  # Update score

        # If the ball goes above the screen, bottom_player has won
        if self.ball.y + 50 >= self.height:
            self.ids.start.text = "Bottom player has won"
            self.server.winner = "bottom_player"
            self.ids.bottom_score.text = str(int(self.ids.bottom_score.text)+1)  # Update score

        self.server.score = [self.ids.top_score.text, self.ids.bottom_score.text]

        return True

    '''
    The positions of the paddles of each player are taken from the server thread in multiplayer_server_thread.py and are
    updated every clock cycle
    '''

    def update(self, dt):
        if not self.check_win():  # If the ball is still in play
            self.ball.move()

            # Update ball coordinates in server thread data
            self.server.data["Ball"] = [self.ball.x, self.ball.y]

            # Update the positions of the paddles on the screen
            self.top_player.center_x = self.server.data["top_player"]
            self.bottom_player.center_x = self.server.data["bottom_player"]

            # Check if ball hits a paddle
            self.bounce()
        else:
            # Return the ball to the centre, stationary
            self.ball.center = self.center
            self.ball.velocity = (0, 0)

            # Start next round after 3 seconds
            Clock.schedule_once(lambda dt: self.serve_ball(), 3)

            # Remove text after 2 seconds
            Clock.schedule_once(lambda dt: setattr(self.server, 'winner', 0), 2)
            Clock.schedule_once(lambda dt: setattr(self.ids.start, 'text', ''), 2)


class ServerApp(App):

    def build(self):
        game = PongGame()
        return game

    def on_stop(self):
        self.root.control.clear()
        sys.exit()


if __name__ == '__main__':
    ServerApp().run()
