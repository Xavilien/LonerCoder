from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from tfimgcontroller import FaceRecognition
from socket import socket, AF_INET, SOCK_STREAM


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

    HOST, PORT = "localhost", 9999
    sock = socket(AF_INET, SOCK_STREAM)

    def __init__(self):
        super(PongGame, self).__init__()
        self.connect()
        self.control = FaceRecognition()
        self.control.start()

    def connect(self):
        self.sock.connect((self.HOST, self.PORT))
        self.sock.sendall(bytes('PLAYER', 'ascii'))

        '''response = int(str(self.sock.recv(1024), 'ascii'))

        if response == 1:
            self.player1, self.player2 = self.player2, self.player1
            self.playerno = 1'''

    def send(self, playerpos):
        self.sock.sendall(bytes(playerpos, 'ascii'))

    def receive(self):
        data = 'GET'
        self.sock.sendall(bytes(data, 'ascii'))
        response = str(self.sock.recv(1024), 'ascii')

        # "player1pos player2pos ballposx ballposy player1score player2score"

    def display(self):
        self.player1.center_y = self.player1pos
        self.player2.center_y = self.player2pos
        self.ball.center_x = self.ballposx
        self.ball.center_y = self.ballposy

    def update(self, dt):
        playerpos = self.height/2 + (self.control.x-0.5) * self.height * 2
        # print(playerpos)

        # Send playerpos
        self.send(str(playerpos))

        # Receive playerpos and opponentpos and ballpos and score
        self.receive()

        # Update diplay
        self.display()


class AIApp(App):
    def build(self):
        game = PongGame()
        return game


if __name__ == '__main__':
    AIApp().run()
