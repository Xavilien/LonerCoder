import socket  # for sockets
import sys  # for exit
import json
from threading import Thread, Event


class Client(Thread):
    s = None
    host = 'localhost'
    port = 8888

    def __init__(self, x, event):
        super(Client, self).__init__()
        self.event = event

        self.create_socket()

        self.x = x
        self.data = []


    def create_socket(self):
        # create an INET, STREAMing socket
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        print('Socket Created')

        # Connect to remote server
        self.s.connect((self.host, self.port))
        print('Socket Connected to ' + self.host + ' on ip ' + self.host)

    def run(self):
        while self.event.is_set():
            try:
                # Set the whole string
                self.s.sendall(str(self.x).encode('utf-8'))
            except socket.error:
                # Send failed
                print('Send failed')
                sys.exit()

            # Now receive data
            data = self.s.recv(4096)
            try:
                self.data = json.loads(data)
            except json.JSONDecodeError:
                pass


if __name__ == "__main__":
    control = Event()
    control.set()
    client = Client(1500, control)
    client.start()
