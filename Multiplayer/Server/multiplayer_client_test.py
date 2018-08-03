import socket  # for sockets
import sys  # for exit
import json
from threading import Thread


class Client(Thread):
    s = None
    host = '10.197.48.168'
    port = 8888

    def __init__(self, x):
        super(Client, self).__init__()
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
        while True:
            print("loop running")
            try:
                # Set the whole string
                self.s.sendall(str(self.x).encode('utf-8'))
            except socket.error:
                # Send failed
                print('Send failed')
                sys.exit()

            # Now receive data
            self.data = json.loads(self.s.recv(4096))


if __name__ == "__main__":
    client = Client()
    client.start()
