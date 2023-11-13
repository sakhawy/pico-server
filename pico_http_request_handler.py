import shutil
import socketserver
import socket
import logging


logger = logging.getLogger(
    'http-server'
)


class PicoHTTPRequestHandler(socketserver.BaseRequestHandler):
    '''
    Servers HTTP files.
    '''
    def __init__(self, request, client_address, server) -> None:
        '''
        Initialize the request handler.
        '''
        super().__init__(request, client_address, server)

    def handle(self) -> None:
        '''
        Main serving logic. Overrides BaseRequestHandler's handle().
        - Create an in-memory file.
        - Follow the protocol:
            - Protocol version line.
            - Headers.
            - Actual file getting served.
        '''
        self.connection: socket.socket = self.request
        with open('index.html', 'rb') as f:
            body = f.read()
        headers = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n'
        response = headers.encode() + body
        self.connection.sendall(response)
