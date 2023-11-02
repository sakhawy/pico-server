#! /usr/bin/env python3
# -*- coding: utf-8 -*-

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

handler = PicoHTTPRequestHandler
with socketserver.TCPServer(('0.0.0.0', 8000), handler) as http:
    logger.info(f'Running on port 8000')
    http.serve_forever()