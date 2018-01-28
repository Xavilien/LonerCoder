import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, Property, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from tfimgcontroller import FaceRecognition
from threading import Thread
from time import time


class PongPaddle(Widget):
    time = Property(0.0)
    highscore = Property(0.0)

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
    jump = 30
    playerpos = 0

    start_time = 0

    def __init__(self):
        super(PongGame, self).__init__()
        self.control = FaceRecognition()
        self.control.start()

        self.t = Thread(target=self.wait)
        self.t.start()

    def wait(self):
        while True:
            if self.control.x is not None:
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

    def serve_ball(self, vel=(2*(0.5-random.random()), -10)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def bounce(self):
        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.ai_agent.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.center_x-25 <= 0) or (self.ball.center_x+25 >= self.width):
            self.ball.velocity_x *= -1

    def check_win(self):
        # went of to a side to score point?
        if self.ball.y < self.y:
            self.serve_ball()
            self.reset()

        if self.ball.y > self.height:
            self.ids.start.text = 'You beat the game!'
            self.reset()
            self.player1.highscore = '>9000'
            self.player1.time = '>9000'

    def reset(self):
        self.player1.highscore = max(self.player1.time, self.player1.highscore)
        self.start_time = time()

    def player_movement(self, dt):
        if abs(self.player1.center_x - self.playerpos) < 90:
            return None
        elif self.playerpos > self.player1.center_x and self.player1.center_x < self.width-100:
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

        # Update position of head
        self.playerpos = self.width/2 + (0.5-self.control.x) * self.width
        # print(self.control.x)

        self.player1.time = round(time() - self.start_time, 1)

        self.ball.move()

        self.bounce()
        self.check_win()


class AI2App(App):
    def build(self):
        game = PongGame()
        return game


if __name__ == '__main__':
    AI2App().run()
