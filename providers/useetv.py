import re

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def get_channel_names(self):
        channel_names = re.findall(
            "https://www.useetv.com/pimages/logo_([a-z0-9]+)_[a-z0-9]+.png",
            (
                self._opener.open("https://www.useetv.com/tv/live")
                .read()
                .decode("utf-8")
            ),
        )
        if not channel_names:
            raise Exception("Failed to get channel names")
        return channel_names

    def get_stream(self, channel_name):
        query = re.search(
            'q[0-9]+ ?= ?"(?P<value>[^"]+)"',
            (
                self._opener.open(
                    f"https://www.useetv.com/livetv/{channel_name}")
                .read()
                .decode("utf-8")
            ),
        )
        if not query:
            raise Exception("Wrong channel name")
        m3u = self._opener.open(b64decode(query.group("value")).decode(
            "utf-8")).read().decode("utf-8").splitlines()
        stream_urls = {}
        stream_quality = None
        for line in m3u:
            if line.startswith("#EXT-X-STREAM-INF"):
                stream_quality = int(
                    re.search('RESOLUTION=[0-9]+x(?P<quality>[0-9]+)', line).group("quality"))
                continue
            if stream_quality and not line.startswith("#"):
                stream_urls[stream_quality] = line
                stream_quality = None
        if not stream_urls:
            raise Exception("Failed to get stream URLs")
        # FIXME Hardcoded stream quality filter
        stream_urls = {k: v for k, v in stream_urls.items() if k <= 480}
        # Take the highest quality stream url available
        channel_url = stream_urls[max(stream_urls.keys())]
        return channel_url

    def get_kodi_headers_suffix(self):
        return "|user-agent=Mozilla"
