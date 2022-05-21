import importlib
import pkgutil
import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.error import HTTPError
from urllib.parse import urlparse
from time import time


class IptvProxyRequestHandler(BaseHTTPRequestHandler):
    _providers = {
        name: importlib.import_module("providers." + name).Provider()
        for finder, name, ispkg
        in pkgutil.iter_modules(path=["providers"])
    }
    _stream_cache = {}

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)

        match_get_stream = re.match( "^/(?P<provider_name>[^/]+)/(?P<channel_name>[^/]+)$", parsed_url.path)

        if match_get_stream:
            provider_name = match_get_stream.group("provider_name")
            channel_name = match_get_stream.group("channel_name")
            self._handle_get_stream(provider_name, channel_name)
            return

        match_get_index = parsed_url.path == "/"

        if match_get_index:
            self._handle_get_index()
            return

        raise HTTPError(404)

    def _handle_get_index(self):
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()
        self.wfile.write("#EXTM3U\n".encode("utf-8"))
        self.wfile.writelines(
            f"#EXT-X-STREAM-INF:BANDWIDTH=0\nhttp://{self.headers.get('Host')}/{provider_name}/{channel_name}{provider_instance.get_kodi_headers_suffix()}\n".encode(
                "utf-8")
            for provider_name, provider_instance in self._providers.items()
            for channel_name in provider_instance.get_channel_names()
        )

    def _handle_get_stream(self, provider_name, channel_name):
        stream_cache_key = provider_name + "/" + channel_name
        stream_cache_value = self._stream_cache.get(stream_cache_key)
        if stream_cache_value and int(time()) < stream_cache_value[0]:
            stream_url = stream_cache_value[1]
        else:
            stream_url = self._providers[provider_name].get_stream(
                channel_name)
            self._stream_cache[stream_cache_key] = (
                int(time()) + 300, stream_url)  # Cache for 5 minutes
        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()
        self.wfile.write("#EXTM3U\n".encode("utf-8"))
        # XXX Fake EXT-X-STREAM-INF BANDWIDTH
        self.wfile.write(
            f"#EXT-X-STREAM-INF:BANDWIDTH=0\n{stream_url}\n".encode(
                "utf-8"
            )
        )


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8888), IptvProxyRequestHandler)
    print("Listening on " + str(server.server_address))
    server.serve_forever()
