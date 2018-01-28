import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, Property, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from tfimgcontroller import FaceRecognition
from threading import Thread
from datetime import datetime, timedelta


class PongPaddle(Widget):
    score = NumericProperty(0)
    time = Property(timedelta(0))
    highscore = Property(timedelta(0))

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.01
            ball.velocity = vel.x, vel.y + offset


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
    expected_y = None
    jump = 30
    alpha = 0
    playerpos = 0

    start_time = None
    time = 0

    def __init__(self):
        super(PongGame, self).__init__()
        self.control = FaceRecognition()
        self.control.start()

        self.t = Thread(target=self.start)
        self.t.start()

    def start(self):
        while True:
            if self.control.x is not None:
                self.serve_ball()
                self.start_time = datetime.now()
                Clock.schedule_interval(self.update, 1.0 / 60.0)
                Clock.schedule_interval(self.agent_movement, 1.0 / 10.0)
                Clock.schedule_interval(self.player_movement, 1.0 / 120.0)
                break

    def serve_ball(self, vel=(10, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def bounce(self):
        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.ai_agent.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

    def check_win(self):
        # went of to a side to score point?
        if self.ball.x < self.x:
            self.ai_agent.score += 1
            # self.alpha -= 0.1
            self.jump += 10
            self.serve_ball(vel=(10, 0))

            self.reset()

        if self.ball.x > self.width:
            self.player1.score += 1
            # self.alpha -= 0.1
            self.jump += 10
            self.serve_ball(vel=(-10, 0))

            self.reset()

    def reset(self):
        self.player1.highscore = max(self.player1.time, self.player1.highscore)
        self.start_time = datetime.now()

    def player_movement(self, dt):
        if abs(self.player1.center_y - self.playerpos) < 90:
            return None
        elif self.player1.center_y < self.playerpos and self.player1.y + 200 < self.height:
            self.player1.center_y += self.jump
        elif self.player1.center_y > self.playerpos and self.player1.y > 0:
            self.player1.center_y -= self.jump

    def agent_movement(self, dt):
        if random.random() > self.alpha:
            if abs(self.ai_agent.center_y - self.expected_y) < 90:
                return None
            elif self.ai_agent.center_y < self.expected_y:
                self.ai_agent.center_y += self.jump
            elif self.ai_agent.center_y > self.expected_y:
                self.ai_agent.center_y -= self.jump
            return None
        else:
            if abs(self.ai_agent.center_y - self.expected_y) < 1000:
                return None
            elif self.ai_agent.center_y < self.expected_y:
                self.ai_agent.center_y += self.jump
            elif self.ai_agent.center_y > self.expected_y:
                self.ai_agent.center_y -= self.jump
            return None

    def update(self, dt):
        delt = (self.width - self.ball.x) / self.ball.velocity_x
        self.expected_y = (self.ball.velocity_y * delt) + self.ball.y
        if self.expected_y > self.height:
            self.expected_y = self.height
        elif self.expected_y < self.y:
            self.expected_y = 0

        # Update position of head
        self.playerpos = self.height/2 + (self.control.x-0.5) * self.height * 2
        # print(self.playerpos)

        self.player1.time = datetime.now() - self.start_time

        self.ball.move()

        self.bounce()
        self.check_win()


class AIApp(App):
    def build(self):
        game = PongGame()
        return game


if __name__ == '__main__':
    AIApp().run()
