import importlib
import pkgutil
import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from time import time


class IptvProxyRequestHandler(BaseHTTPRequestHandler):
    _providers = {
        name: importlib.import_module("providers." + name).Provider()
        for finder, name, ispkg
        in pkgutil.iter_modules(path=["providers"])
    }
    _playlist_cache = {}

    def do_HEAD(self):
        parsed_url = urlparse(self.path)

        match_get_stream = re.match(
            "^/(?P<provider_name>[^/]+)/(?P<channel_name>[^/]+)$", parsed_url.path)

        if match_get_stream:
            provider_name = match_get_stream.group("provider_name")
            channel_name = match_get_stream.group("channel_name")
            self._handle_get_stream(provider_name, channel_name, True)
            return

        match_get_index = parsed_url.path == "/"

        if match_get_index:
            self._handle_get_index()
            return

    def do_GET(self):
        parsed_url = urlparse(self.path)

        match_get_stream = re.match(
            "^/(?P<provider_name>[^/]+)/(?P<channel_name>[^/]+)$", parsed_url.path)

        if match_get_stream:
            provider_name = match_get_stream.group("provider_name")
            channel_name = match_get_stream.group("channel_name")
            self._handle_get_stream(provider_name, channel_name)
            return

        match_get_index = parsed_url.path == "/"

        if match_get_index:
            self._handle_get_index()
            return

        self.send_response(404)

    # TODO Break up method
    def _handle_get_stream(self, provider_name, channel_name, is_head=False):
        playlist_cache_key = provider_name + "/" + channel_name
        playlist_cache_value = self._playlist_cache.get(playlist_cache_key)
        playlist = None
        if playlist_cache_value and int(time()) < playlist_cache_value[0]:
            playlist = playlist_cache_value[1]
        if not playlist:
            playlist = self._providers[provider_name].get_channel_playlist(
                channel_name)
            if playlist.startswith(str("#EXTM3U")):
                self._playlist_cache[playlist_cache_key] = (
                    int(time()) + 300, playlist)  # Cache m3u playlist for 5 minutes
        if playlist.startswith(str("#EXTM3U")):
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.end_headers()
            if is_head:
                return
            video_resolution = 0
            # FIXME Hardcoded video resolution limit
            for line in playlist.splitlines():
                if line.startswith("#EXT-X-STREAM-INF"):
                    video_resolution = int(
                        re.search('RESOLUTION=[0-9]+x(?P<height>[0-9]+)', line).group("height"))
                    if video_resolution <= 480:
                        self.wfile.write(f"{line}\n".encode("utf-8"))
                else:
                    if video_resolution <= 480:
                        self.wfile.write(f"{line}\n".encode("utf-8"))
                    video_resolution = 0
        elif playlist.startswith(str('<MPD')):
            body = playlist.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/dash+xml")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if is_head:
                return
            self.wfile.write(body)
        else:
            self.send_response(500)

    def _handle_get_index(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.apple.mpegurl")
        self.end_headers()
        self.wfile.write("#EXTM3U\n".encode("utf-8"))
        for provider_name, provider_instance in self._providers.items():
            for channel_name in provider_instance.get_channel_names():
                self.wfile.write((
                    "#EXT-X-STREAM-INF:BANDWIDTH=0\n"
                    f"{provider_instance.get_kodi_props(channel_name)}"
                    f"http://{self.headers.get('Host')}/{provider_name}/{channel_name}{provider_instance.get_kodi_url_suffix()}\n"
                ).encode("utf-8"))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8888), IptvProxyRequestHandler)
    print("Listening on " + str(server.server_address))
    server.serve_forever()
