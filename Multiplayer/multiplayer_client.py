from threading import Thread
import json
import request
import time


class Client(Thread):

    def __init__(self, host, port):
        super(Client, self).__init__()
        self.HOST = host
        self.PORT = port
        self.data = None
        self.playerID = None

    def run(self):
        self.player()
        while True:
            time.sleep(0.2)
            self.check()
            print(self.data)

    def check(self):
        url = 'http://%s:%d' % (self.HOST, self.PORT)
        with request.get(url, params={"player": 0}) as r:
            self.data = json.loads(r.read().decode("utf-8"))

    def player(self):
        url = 'http://%s:%d' % (self.HOST, self.PORT)
        with request.get(url, params={"player": 1}) as r:
            self.playerID = json.loads(r.read().decode("utf-8"))["playerID"]
            print("You are player " + str(self.playerID))

if __name__ == '__main__':
    c = Client('localhost', 8000)
    c.start()
