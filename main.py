
import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from api.useetv import UseeTvApi

class IptvRequestHandler(BaseHTTPRequestHandler):
    def initialize():
        IptvRequestHandler.Api = UseeTvApi()
    def do_GET(self):
        try:
            url = None
            q = re.match('^/([^/]+)$', self.path)
            if q:
                channel = q.group(1)
                url = self.Api.get_url(channel)
            if url: 
                self.send_response(200)
                self.send_header('Content-type','application/vnd.apple.mpegurl')
                self.end_headers()
                self.wfile.write(url.encode("utf-8"))
            else:
                self.send_error(404)
        except:
            self.send_error(404)

if __name__ == "__main__":
    IptvRequestHandler.initialize()
    server = HTTPServer(('127.0.0.1',8080), IptvRequestHandler)
    server.serve_forever()
