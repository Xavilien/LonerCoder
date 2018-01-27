import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
import controller


class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.2
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
    jump = 50
    alpha = 0.9

    def __init__(self):
        super(PongGame, self).__init__()
        self.serve_ball()
        self.control = controller.FacialRecognition()

        # self.bind_keyboard()

    '''
    def bind_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):  # Function for keyboard events
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Allow for key presses to activate some buttons
        """
        if keycode[1] == 'up':
            self.player1.center_y += self.jump

        elif keycode[1] == 'down':
            self.player1.center_y -= self.jump

        return keyboard, text, modifiers
    '''

    def serve_ball(self, vel=(10, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

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
        self.ball.move()

        delt = (self.width - self.ball.x) / (self.ball.velocity_x)
        self.expected_y = (self.ball.velocity_y * delt) + self.ball.y
        if self.expected_y > self.width:
            self.expected_y = self.width
        elif self.expected_y < self.y:
            self.expected_y = 0

        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.ai_agent.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went of to a side to score point?
        if self.ball.x < self.x:
            self.ai_agent.score += 1
            self.alpha -= 0.1
            self.jump += 10
            self.serve_ball(vel=(10, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.alpha -= 0.1
            self.jump += 10
            self.serve_ball(vel=(-10, 0))

        # movement of player paddle
        self.player1.y = int(self.control.face_x * self.height)

    """
    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.ai_agent.center_y = touch.y
    """


class AIApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0/120.0)
        Clock.schedule_interval(game.agent_movement, 1.0/10.0)
        Clock.schedule_interval(game.control.capture, 1.0/10.0)
        return game


if __name__ == '__main__':
    AIApp().run()