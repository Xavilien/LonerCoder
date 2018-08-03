import socket  # for sockets
import sys  # for exit
from threading import Thread


class Client(Thread):
    s = None
    host = '10.197.48.168'
    port = 8888

    def __init__(self):
        super(Client, self).__init__()
        self.create_socket()

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
            # Send some data to remote server
            message = input()

            try:
                # Set the whole string
                self.s.sendall(message.encode('utf-8'))
            except socket.error:
                # Send failed
                print('Send failed')
                sys.exit()

            # Now receive data
            reply = self.s.recv(4096).decode('utf-8')

            print(reply)


if __name__ == "__main__":
    client = Client()
    client.start()
