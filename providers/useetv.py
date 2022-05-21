import re
import time

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, HTTPError
from time import time


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._stream_url_cache = {}

    def get_kodi_url_suffix(self):
        return "|user-agent=Mozilla"

    def get_channel_names(self):
        channel_list = re.findall(
            "https://www.useetv.com/pimages/logo_([a-z0-9]+)_[a-z0-9]+.png",
            (
                self._opener.open("https://www.useetv.com/tv/live")
                .read()
                .decode("utf-8")
            ),
        )
        if not channel_list:
            raise HTTPError(404)
        return channel_list

    def get_stream(self, channel_name):
        c = self._stream_url_cache.get(channel_name)
        if c and int(time()) < c[0]:
            channel_url = c[1]
        else:
            q = re.search(
                'q[0-9]+ ?= ?"(?P<value>[^"]+)"',
                (
                    self._opener.open(
                        f"https://www.useetv.com/livetv/{channel_name}")
                    .read()
                    .decode("utf-8")
                ),
            )
            if not q:
                raise HTTPError(404)
            m3u = self._opener.open(b64decode(q.group("value")).decode(
                "utf-8")).read().decode("utf-8").splitlines()
            stream_urls = {}
            stream_quality = None
            for line in m3u:
                if line.startswith("#EXT-X-STREAM-INF"):
                    stream_quality = int(
                        re.search('RESOLUTION=[0-9]+x(?P<quality>[0-9]+)', line).group("quality"))
                    continue
                if stream_quality and line.startswith("https://"):
                    stream_urls[stream_quality] = line
                    stream_quality = None
            if not stream_urls:
                raise HTTPError(404)
            # FIXME Hardcoded stream quality filter
            stream_urls = {k: v for k, v in stream_urls.items() if k <= 480}
            # Take the highest quality stream url available
            channel_url = stream_urls[max(stream_urls.keys())]
            self._stream_url_cache[channel_name] = (
                int(time()) + 300, channel_url)  # Cache for 5 minutes
        return channel_url
