#!/usr/bin/env python3
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

data = [None, None, 0, 0, 0, 0]
mapdict = {}


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        # message = threading.currentThread().getName()
        self.wfile.write(bytes(json.dumps({'data': data}), "utf8"))
        return

    def do_POST(self):
        self.send_response(200)

    def do_PLAYER(self):
        self.send_response(200)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


if __name__ == '__main__':

    server = ThreadedHTTPServer(('localhost', 8000), Handler)
    print('Starting server, use <Ctrl-C> to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


