import socket
import sys
from threading import Thread


class Connection(Thread):
    def __init__(self, connection, address):
        super(Connection, self).__init__()
        self.connection = connection
        self.address = address
        self.x = None
        self.data = None

    def run(self):
        while True:
            # Receiving from client
            try:
                data = self.connection.recv(1024).decode('utf-8')
                self.x = int(data)

                self.connection.sendall(self.data.encode('utf-8'))

            except socket.error as msg:
                print(msg)
                break


class Server(Thread):

    def __init__(self):
        super(Server, self).__init__()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_setup()

        self.data = {"Ball": [], "top_player": None, "bottom_player": None}  # Positions of ball and both players

        self.winner = None  # If the game has a winner

        self.top_player = None
        self.bottom_player = None

    def socket_setup(self):
        host = ''  # Symbolic name meaning all available interfaces
        port = 8000  # Arbitrary non-privileged port

        print('Socket created')

        # Bind socket to local host and port
        try:
            self.s.bind((host, port))
        except socket.error as msg:
            print('Bind failed. Error: ' + str(msg))
            sys.exit()
        print("Bind succeeded")

        # Start listening on socket
        self.s.listen(10)
        print("Listening...")

    def run(self):
        while True:
            if self.top_player is None:
                connection, address = self.s.accept()
                print(address[0] + ':' + str(address[1]))
                self.top_player = Connection(connection, address)

                data = self.top_player.connection.recv(1024).decode('utf-8')
                self.top_player.x = int(data)
                self.data["top_player"] = self.top_player.x
                self.top_player.connection.sendall("top_player".encode('utf-8'))

                self.top_player.start()
                print("Top started")

            elif self.bottom_player is None:
                connection, address = self.s.accept()
                print(address[0] + ':' + str(address[1]))
                self.bottom_player = Connection(connection, address)

                data = self.bottom_player.connection.recv(1024).decode('utf-8')
                self.bottom_player.x = int(data)
                self.data["bottom_player"] = self.bottom_player.x
                self.bottom_player.connection.sendall("bottom_player".encode('utf-8'))

                self.bottom_player.start()
                print("Bottom started")

            else:
                self.data["top_player"] = self.top_player.x
                self.data["bottom_player"] = self.bottom_player.x

                self.top_player.data = [self.data["Ball"], self.data["bottom_player"]]
                self.bottom_player.data = [self.data["Ball"], self.data["top_player"]]


if __name__ == '__main__':
    server = Server()
    server.start()
