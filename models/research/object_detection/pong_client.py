from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from tfimgcontroller import FaceRecognition
from socket import socket, AF_INET, SOCK_STREAM
from kivy.clock import Clock
from threading import Thread


class PongPaddle(Widget):
    score = NumericProperty(0)


class PongBall(Widget):
    pass


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    player1pos = 0
    player2pos = 0
    ballposx = 0
    ballposy = 0

    playerno = 0

    HOST, PORT = "192.168.43.122", 7000
    sock = socket(AF_INET, SOCK_STREAM)

    def __init__(self):
        super(PongGame, self).__init__()

        self.ready = False
        self.connect()
        self.control = FaceRecognition()
        self.control.start()

        self.connection = Thread(target=self.receive)

        self.t = Thread(target=self.start)
        self.t.start()

    def start(self):
        while self.control.x is None or not self.ready:
            print(self.control.x, self.ready)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.connection.start()

    def connect(self):
        self.sock.connect((self.HOST, self.PORT))
        self.sock.sendall(bytes('PLAYER', 'ascii'))
        response = str(self.sock.recv(1024), 'ascii')
        self.ready = bool(response)

        '''response = int(str(self.sock.recv(1024), 'ascii'))

        if response == 1:
            self.player1, self.player2 = self.player2, self.player1
            self.playerno = 1'''

    def send(self, playerpos):
        self.sock.sendall(bytes(playerpos, 'ascii'))
        response = str(self.sock.recv(1024), 'ascii')

    def receive(self):
        while True:
            data = 'GET'
            self.sock.sendall(bytes(data, 'ascii'))

            # "player1pos player2pos ballposx ballposy player1score player2score"
            response = [int(i) for i in str(self.sock.recv(1024), 'ascii').split()]

            if len(response) == 6:
                self.player1pos = response[0]
                self.player2pos = response[1]
                self.ballposx = response[2]
                self.ballposy = response[3]
                self.player1.score = response[4]
                self.player2.score = response[5]

    def display(self):
        self.player1.center_y = self.player1pos
        self.player2.center_y = self.player2pos
        self.ball.center_x = self.ballposx
        self.ball.center_y = self.ballposy

    def update(self, dt):
        playerpos = self.height/2

        if self.control.x is not None:
            playerpos += (self.control.x-0.5) * self.height * 2

        # print(playerpos)

        # Send playerpos
        self.send(str(playerpos))

        # Update diplay
        self.display()


class AIApp(App):
    def build(self):
        game = PongGame()
        return game


if __name__ == '__main__':
    AIApp().run()
