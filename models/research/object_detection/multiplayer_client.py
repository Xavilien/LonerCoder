from threading import Thread
import requests


class Client(Thread):

    def __init__(self, host, port):
        super(Client, self).__init__()
        self.HOST = host
        self.PORT = port
        self.data = None

    def run(self):
        while True:
            self.check()

    def check(self):
        r = requests.get('http://%s:%d' %(self.HOST, self.PORT))
        self.data = r.json()['data']
        print(self.data)


c = Client('localhost', 8000)
c.start()
