#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import socket
import http.server
from http import HTTPStatus
import logging
import io
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(
    'http-server'
)


class PicoTCPServer:
    def __init__(
        self, 
        socket_address: tuple[str, int], 
        request_handler: PicoHTTPRequestHandler
    ) -> None:
        self.request_handler = request_handler
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(socket_address)

        self.sock.listen()

    def serve_forever(self) -> None:
        while True:
            conn, addr = self.sock.accept()

            with conn:
                logger.info(f'Accepted connection from {addr}')
                request_stream = conn.makefile('rb')
                self.request_handler(
                    request_stream=request_stream,
                    client_address=addr,
                    client=conn,
                    server=self.sock
                )
            logger.info(f'Closed connection from {addr}')

    def __enter__(self) -> PicoTCPServer:
        return self

    def __exit__(self, *args) -> None:
        self.sock.close()

class PicoHTTPRequestHandler:
    '''
    Server static files as-is. Only supports GET and HEAD.
    Any other method will return 405 except POST, which will return 403.

    The version is assumed to be HTTP/1.1.
    '''
    def __init__(
        self, 
        request_stream: io.BufferedIOBase, 
        client_address: tuple[str, int],
        client: socket.socket,
        server: socket.socket
    ) -> None:
        self.request_stream = request_stream
        self.client_address = client_address
        self.server = server
        self.client = client
        self.command = ''
        self.path = ''
        self.headers = {
            'Content-Type': 'text/html',
            'Content-Length': '0',
            'Connection': 'close'
        }
        self.data = ''
        self.handle()

    def handle(self) -> None:
        '''Handles the request.'''
        # anything but GET or HEAD will return 405
        # POST will return a 403

        # parse the request to populate
        # self.command, self.path, self.headers
        self._parse_request()
        
        if not self._validate_path():
            return self._handle_404()

        if self.command not in ('GET', 'HEAD'):
            return self._handle_405()

        if self.command == 'POST':
            return self._handle_403()
        
        method = getattr(self, f'handle_{self.command}') 
        method()

    def handle_GET(self) -> None:
        '''
        Writes headers and the file to the socket.
        '''
        self.handle_HEAD()

        with open(self.path, 'rb') as f:
            body = f.read()

        self.client.sendall(body)

    def handle_HEAD(self) -> None:
        '''
        Writes headers to the socket.
        '''
        # default to 200
        self._write_response_line(200)
        self._write_headers(
            **{
                'Content-Length': os.path.getsize(self.path)
            }
        )

    def _write_response_line(self, status_code: int) -> None:
        reponse_line = f'HTTP/1.1 {status_code} {HTTPStatus(status_code).phrase}'
        logger.info(reponse_line.encode())
        self.client.sendall(reponse_line.encode())

    def _write_headers(self, *args, **kwargs) -> None:
        headers_copy = self.headers.copy()
        headers_copy.update(**kwargs)
        header_lines = '\r\n'.join(
            f'{k}: {v}' for k, v in headers_copy.items()
        )
        logger.info(header_lines.encode())
        self.client.sendall(header_lines.encode())
        # mark the end of the headers
        self.client.sendall(b'\r\n\r\n')

    def _parse_request(self) -> None:
        # parse the request line
        logger.info('Parsing request line')
        requestline = self.request_stream.readline().decode()
        requestline = requestline.rstrip('\r\n')
        logger.info(requestline)

        self.command = requestline.split(' ')[0]
        self.path = requestline.split(' ')[1]

        # parse the headers
        headers = {} 
        line = self.request_stream.readline().decode()
        while line not in ('\r\n', '\n', '\r', ''):
            header = line.rstrip('\r\n').split(': ')
            headers[header[0]] = header[1]
            line = self.request_stream.readline().decode()

        logger.info(headers)

    def _validate_path(self) -> bool:
        '''
        Validates the path. Returns True if the path is valid, False otherwise.
        '''
        # the path can either be a file or a directory
        # if it's a directory, look for index.html
        # if it's a file, serve it
        self.path = os.path.join(os.getcwd(), self.path.lstrip('/'))
        if os.path.isdir(self.path):
            self.path = os.path.join(self.path, 'index.html')
        elif os.path.isfile(self.path):
            pass

        if not os.path.exists(self.path):
            return False 

        return True 

    def _handle_404(self) -> None:
        '''NOT FOUND'''
        self._write_response_line(404)
        self._write_headers()

    def _handle_405(self) -> None:
        '''NON IMPLEMENTED COMMANDS'''
        self._write_response_line(405)
        self._write_headers()

    def _handle_403(self) -> None:
        '''FORBIDDEN POST'''
        self._write_response_line(403)
        self._write_headers()


with PicoTCPServer(('0.0.0.0', 8000), PicoHTTPRequestHandler) as http:
    logger.info(f'Running on port 8000')
    http.serve_forever()
