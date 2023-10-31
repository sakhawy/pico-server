import http.server
import socketserver
import logging

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(
    'http-server'
)

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(('0.0.0.0', 8000), handler) as http:
    logger.info(f'Running on port 8000')
    http.serve_forever()