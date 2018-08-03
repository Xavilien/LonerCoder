import socket
import sys
from threading import Thread


class Connection(Thread):
    def __init__(self, connection, address):
        super(Connection, self).__init__()
        self.connection = connection
        self.address = address

    def run(self):
        while True:
            # Receiving from client
            try:
                data = self.connection.recv(1024).decode('utf-8')
                reply = 'OK...' + data

                self.connection.sendall(reply.encode('utf-8'))

            except socket.error as msg:
                print(msg)
                break


class Server(Thread):

    def __init__(self):
        super(Server, self).__init__()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_setup()

        self.data = {"Ball": []}

    def socket_setup(self):
        host = ''  # Symbolic name meaning all available interfaces
        port = 8888  # Arbitrary non-privileged port

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
            connection, address = self.s.accept()
            print(address[0] + ':' + str(address[1]))
            thread = Connection(connection, address)
            thread.start()
            print("Thread started")


if __name__ == '__main__':
    server = Server()
    server.start()
