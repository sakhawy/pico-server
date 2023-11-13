#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import socket
import http.server
import socketserver
import logging

from pico_http_request_handler import PicoHTTPRequestHandler

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
        request_handler: http.server.SimpleHTTPRequestHandler
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
                self.request_handler(conn, addr, self.sock)
            logger.info(f'Closed connection from {addr}')

    def __enter__(self) -> PicoTCPServer:
        return self

    def __exit__(self, *args) -> None:
        self.sock.close()


with PicoTCPServer(('0.0.0.0', 8000), http.server.SimpleHTTPRequestHandler) as http:
    logger.info(f'Running on port 8000')
    http.serve_forever()
