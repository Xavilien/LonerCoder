import random
import socket
import threading
import socketserver
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock


data = [None, None, 0, 0, 0, 0]
mapdict = {}


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    global data
    global mapdict

    def handle(self):
        self.reqinput = str(self.request.recv(1024), 'ascii').split()
        command = self.reqinput[0]
        method = "do_" + command
        do = getattr(self, method)
        do()

    def do_GET(self):
        self.request.sendall(bytes(" ".join([str(i) for i in data]), 'ascii'))

    def do_POST(self):
        data[mapdict[self.client_address[0]]] = float(self.reqinput[1])  # Update player positions

    def do_PLAYER(self):
        if len(mapdict.keys()) == 0:
            mapdict[self.client_address[0]] = 0
        else:
            mapdict[self.client_address[0]] = 1


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class PongPaddle(Widget):
    score = NumericProperty(0)

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
    global data
    global mapdict

    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    jump = 30

    HOST, PORT = "localhost", 8000
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()


    def __init__(self):
        super(PongGame, self).__init__()
        self.t = threading.Thread(target=self.start)
        self.t.start()

    def start(self):
        while True:
            if (data[0] is not None) and (data[1] is not None):
                self.serve_ball()
                Clock.schedule_interval(self.update, 1.0 / 60.0)
                Clock.schedule_interval(self.player1_movement, 1.0 / 10.0)
                Clock.schedule_interval(self.player2_movement, 1.0 / 10.0)
                break


    def serve_ball(self, vel=(10, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def bounce(self):
        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

    def check_win(self):
        # went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.jump += 10
            self.serve_ball(vel=(10, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.jump += 10
            self.serve_ball(vel=(-10, 0))

    def player1_movement(self, dt):
        if abs(self.player1.center_y - data[0]) < 90:
            return None
        elif self.player1.center_y < data[0]:
            self.player1.center_y += self.jump
        elif self.player1.center_y > data[0]:
            self.player1.center_y -= self.jump

    def player2_movement(self, dt):
        if abs(self.player2.center_y - data[1]) < 90:
            return None
        elif self.player2.center_y < data[1]:
            self.player2.center_y += self.jump
        elif self.player2.center_y > data[1]:
            self.player2.center_y -= self.jump

    def update_data(self):
        data[2] = self.ball.x
        data[3] = self.ball.y
        data[4] = self.player1.score
        data[5] = self.player2.score

    def update_game(self, dt):
        self.ball.move()
        self.bounce()
        self.check_win()
        self.update_data()

class AIApp(App):
    def build(self):
        game = PongGame()
        return game


if __name__ == '__main__':
    AIApp().run()
