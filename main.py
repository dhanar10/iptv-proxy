import importlib
import pkgutil
import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class IptvProxyRequestHandler(BaseHTTPRequestHandler):
    Providers = {}

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()

    def do_GET(self):
        if self.handle_get_index():
            return
        elif self.handle_get_stream():
            return

    def handle_get_index(self):
        url_match = urlparse(self.path).path == "/"
        if not url_match:
            return False
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()
        self.wfile.write("#EXTM3U\n".encode("utf-8"))
        self.wfile.writelines(
            f"#EXT-X-STREAM-INF:BANDWIDTH=0\nhttp://{self.headers.get('Host')}/{provider_name}/{channel_name}{provider_instance.get_kodi_url_suffix()}\n".encode(
                "utf-8")
            for provider_name, provider_instance in self.Providers.items()
            for channel_name in provider_instance.get_channel_names()
        )
        return True

    def handle_get_stream(self):
        url_match = re.match(
            "^/(?P<provider_name>[^/]+)/(?P<channel_name>[^/]+)$", urlparse(self.path).path)
        if not url_match:
            return False
        provider_name = url_match.group("provider_name")
        channel_name = url_match.group("channel_name")
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()
        self.wfile.write("#EXTM3U\n".encode("utf-8"))
        # XXX Fake EXT-X-STREAM-INF BANDWIDTH
        self.wfile.write(
            f"#EXT-X-STREAM-INF:BANDWIDTH=0\n{self.Providers[provider_name].get_stream(channel_name)}\n".encode(
                "utf-8"
            )
        )
        return True


if __name__ == "__main__":
    IptvProxyRequestHandler.Providers = {
        name: importlib.import_module("providers." + name).Provider()
        for finder, name, ispkg
        in pkgutil.iter_modules(path=["providers"])
    }
    server = HTTPServer(("0.0.0.0", 8888), IptvProxyRequestHandler)
    print("Listening on " + str(server.server_address))
    server.serve_forever()
