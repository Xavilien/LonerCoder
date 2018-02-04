import random
from threading import Thread
from time import time

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, Property, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector
from tfimgcontroller import FaceDetection


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
            vel = bounced * 1.05
            ball.velocity = vel.x + offset, vel.y


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    ai_agent = ObjectProperty(None)

    expected_x = None
    playerpos = 0
    jump = 30  # Distance the paddles can move each clock cycle

    start_time = 0  # Allow us to calculate time elapsed since game started

    def __init__(self):
        super(PongGame, self).__init__()
        self.detector = FaceDetection()
        self.detector.start()

        self.t = Thread(target=self.wait)
        self.t.start()

    '''
    Wait for the facedetection to be loaded so that the game doesn't start when it is not ready
    '''

    def wait(self):
        while True:
            if self.detector.x is not None:
                self.ball.opacity = 1
                self.ids.start.text = 'Starting'
                Clock.schedule_once(self.start, 2)
                break

    def start(self, dt):
        self.ids.start.text = ''
        self.serve_ball()
        self.start_time = time()
        Clock.schedule_interval(self.update, 1.0 / 30.0)
        Clock.schedule_interval(self.agent_movement, 1.0 / 30.0)
        Clock.schedule_interval(self.player_movement, 1.0 / 30.0)

    '''
    The ball is not served perpendicular to the paddle so that the player cannot stall by not moving
    '''

    def serve_ball(self, vel=(2 * (0.5 - random.random()), -10)):
        self.ball.center = self.center
        self.ball.velocity = vel  # Get the ball to start moving

    '''
    Check if the ball has collided with the paddles or the walls
    '''

    def bounce(self):
        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.ai_agent.bounce_ball(self.ball)

        # bounce ball off left or right
        if (self.ball.center_x - 25 <= 0) or (self.ball.center_x + 25 >= self.width):
            self.ball.velocity_x *= -1  # Change direction so that ball doesn't go off screen

    def check_win(self):
        # went of to a side to end game?
        if self.ball.y < self.y:
            self.serve_ball()
            self.reset()

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

    '''
    Paddles only move if the x-coordinate of the person is far enough from the center of the paddle so that it is easier
    to keep the paddle still and control it

    Paddles move a bit each clock cycle so that the paddles do not seem to 'jump'
    '''

    def player_movement(self, dt):
        if abs(self.player1.center_x - self.playerpos) < 90:
            return None
        elif self.playerpos > self.player1.center_x and self.player1.center_x < self.width - 100:
            self.player1.center_x += self.jump
        elif self.playerpos < self.player1.center_x and self.player1.center_x > 100:
            self.player1.center_x -= self.jump

    def agent_movement(self, dt):
        if abs(self.ai_agent.center_x - self.expected_x) < 90:
            return None
        elif self.ai_agent.center_x < self.expected_x:
            self.ai_agent.center_x += self.jump
        elif self.ai_agent.center_x > self.expected_x:
            self.ai_agent.center_x -= self.jump

    def predict(self):
        delt = (self.height - self.ball.y) / self.ball.velocity_y
        self.expected_x = (self.ball.velocity_x * delt) + self.ball.x
        if self.expected_x > self.width:
            self.expected_x = self.width
        elif self.expected_x < self.x:
            self.expected_x = 0

    def update(self, dt):
        self.predict()

        # Update position of head by adding the offset to half the width
        sensitivity = 2
        offset = (0.5 - self.detector.x) * self.width  # How far the head is from the center
        self.playerpos = self.width / 2 + offset * sensitivity
        # print(self.detector.x)

        # Update the stopwatch with the time elapsed
        self.player1.time = round(time() - self.start_time, 1)
        self.player1.highscore = max(self.player1.time, self.player1.highscore)

        self.ball.move()

        self.bounce()
        self.check_win()


class AI2App(App):
    def build(self):
        game = PongGame()
        return game


if __name__ == '__main__':
    AI2App().run()
