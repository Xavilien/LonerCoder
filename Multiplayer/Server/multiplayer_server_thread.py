#!/usr/bin/env python3
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import json


data = {"ball": None}


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        params = parse_qs(self.rfile.read(int(self.headers.get("Content-length", 0))).decode("utf-8")) # is a dictionary
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps({'data': data}), "utf-8"))
        return

    def do_POST(self):
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


