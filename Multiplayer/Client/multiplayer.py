import threading
from tfimgcontroller import FaceDetection
import sys

from multiplayer_client_thread import Client

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
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
        self.player = None  # The player's paddle is assigned to this after we find out if the player is top or bottom
        self.opponent = None  # This is assigned the other paddle
        self.client = None  # The conncetion client
        self.player_identity = None  # Whether player is top_player or bottom_player

        self.detector = FaceDetection(self.control)  # Allow us to control the paddle using the player's body
        self.detector.start()

        self.waiting = threading.Thread(target=self.wait)  # Wait for the game to load and connect
        self.waiting.start()

    '''
    Connect to the server and set up the game
    '''
    def wait(self):
        # Make sure that the game does not start until the face detector is ready
        while self.detector.x is None:
            pass

        # Connect to the server and send a request to the server to find out if the player is top or bottom
        self.client = Client(self.top_player.center_x, self.control)
        self.client.s.sendall(str(self.x).encode('utf-8'))
        self.player_identity = self.client.s.recv(4096).decode("utf8")

        # Let the player know if he/she is the top player or bottom player and put a text label on the paddle
        if self.player_identity == "top_player":
            self.player = self.top_player
            self.opponent = self.bottom_player
            text = "top"
            self.ids.top_text.text = "YOU"
        elif self.player_identity == "bottom_player":
            self.player = self.bottom_player
            self.opponent = self.top_player
            text = "bottom"
            self.ids.bottom_text.text = "YOU"
        else:
            raise Exception("player not assigned")

        self.ids.start.text = 'You are the %s player' % text
        Clock.schedule_once(lambda dt: setattr(self.ids.start, 'text', ''), 3)  # Text disappears after 3 seconds

        self.client.start()  # Start the connection thread that continuously pings the server for updates

        # Wait for the other player to connect
        while not len(self.client.data) or self.client.data[1] == -1:
            self.player_movement()

        # When everythning is ready, the game starts
        if self.control.is_set():
            self.ball.opacity = 1
            Clock.schedule_once(lambda dt: setattr(self.ids.start, 'text', 'Starting'), 3)
            Clock.schedule_once(self.start, 4)

    '''
    Start the game by clearing the screen and starting the game loop
    '''
    def start(self, dt):
        self.ids.start.text = ''
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    '''
    Reset the game by returning the player's and the opponent's paddles to the center
    '''
    def reset(self):
        self.player.center_x = self.width/2
        self.opponent.center_x = self.width/2

    '''
    Update the position of the player's paddle based on the position of the player's body
    '''
    def player_movement(self):
        # Update position of head by adding the offset to half the width
        sensitivity = 2

        # 0 <= self.detector.x <= 1
        # So this get's how far the player's body is from the center of the screen in terms of pixels
        # -self.width/2 < offset < self.width/2
        offset = (0.5 - self.detector.x) * self.width

        # Get the position of the player's body in terms of pixels
        # Increase sensitivity of the detector so that the player does not have to move so much
        playerpos = self.width / 2 + offset * sensitivity

        paddle_center = self.player.center_x  # Centre of the paddle
        width = self.ids.player_bottom.size[0]/2  # Half the size of the paddle

        # We only move if the position of the body is outside of the paddle
        # This is to prevent the paddle from "vibrating" on the spot randomly as the position of the player's body that
        # is detected by the detector fluctuates frequently
        if abs(paddle_center - playerpos) < width:
            return None
        elif playerpos > paddle_center and paddle_center < self.width - width:
            self.player.center_x += dp(20)
        elif playerpos < paddle_center and paddle_center > width:
            self.player.center_x -= dp(20)

        self.client.x = self.player.center_x  # Update the data that is sent to the server

    '''
    Update the position of the opponent's paddle based on the data from the server
    '''
    def opponent_movement(self):
        self.opponent.center_x = self.client.data[1]

    '''
    Update the position of the ball based on the data from the server
    '''
    def ball_movement(self):
        self.ball.x = self.client.data[0][0]
        self.ball.y = self.client.data[0][1]

    def check_win(self):
        winner = self.client.data[2]

        if winner != 0:
            if winner == self.player_identity:
                self.ids.start.text = 'You have won'
            else:
                self.ids.start.text = 'You have lost'
        else:
            self.ids.start.text = ""

        if winner == "top_player":
            self.ids.top_score.text = str(int(self.ids.top_score.text)+1)
        elif winner == "bottom_player":
            self.ids.bottom_score.text = str(int(self.ids.bottom_score.text)+1)

    '''
    Update the game at every clock cycle
    '''
    def update(self, dt):
        self.player_movement()
        self.opponent_movement()
        self.ball_movement()
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
