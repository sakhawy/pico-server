import shutil
import socketserver
import socket

class PicoHTTPRequestHandler(socketserver.BaseRequestHandler):
    '''
    Servers HTTP files.
    '''
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
        wfile = self.connection.makefile('wb', 2**16)
        wfile.write(b'HTTP/1.1 200 OK\r\n')
        wfile.write(b'Content-Type: text/html\r\n')
        wfile.write(b'\r\n')
        with open('index.html', 'rb') as f:
            wfile.write(f.read())

        wfile.flush()
        wfile.close()
