import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from api.useetv import UseeTvApi


class IptvRequestHandler(BaseHTTPRequestHandler):
    def initialize():
        IptvRequestHandler.Api = UseeTvApi()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()

    def do_GET(self):
        try:
            if self.handle_index():
                return
            elif self.handle_channel():
                return
        except:
            pass
        self.send_error(404)

    def handle_index(self):
        q = self.path == "/"
        if not q:
            return False
        base_url = f"http://{self.headers.get('Host')}"
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()
        self.wfile.writelines(
            f"{line}\n".encode("utf-8") for line in ["#EXTM3U"]
        )
        self.wfile.writelines(
            [
                f"#EXT-X-STREAM-INF:BANDWIDTH=0\n{base_url}/{line}|user-agent=Mozilla\n".encode("utf-8")
                for line in self.Api.get_channel_list()
            ]  # XXX Fake EXT-X-STREAM-INF BANDWIDTH, Kodi user-agent=Mozilla
        )
        return True

    def handle_channel(self):
        q = re.match("^/(?P<channel>[^/]+)$", self.path)
        if not q:
            return False
        channel = q.group("channel")
        url = self.Api.get_url(channel)
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()
        self.wfile.writelines(f"{line}\n".encode("utf-8") for line in ["#EXTM3U"])
        self.wfile.write(
            f"#EXT-X-STREAM-INF:BANDWIDTH=0\n{url}\n".encode("utf-8")
        )  # XXX Fake EXT-X-STREAM-INF BANDWIDTH
        return True


if __name__ == "__main__":
    IptvRequestHandler.initialize()
    server = HTTPServer(("0.0.0.0", 8080), IptvRequestHandler)
    server.serve_forever()
