import re

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor

class UseeTvApi:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def get_url(self, channel):
        html = (
            self._opener.open(f"https://www.useetv.com/livetv/{channel}")
            .read()
            .decode("utf-8")
        )
        q = re.search('q[0-9]+="([^"]+)"', html)
        if not q:
            return None
        playlist_url = b64decode(q.group(1)).decode("utf-8")
        playlist_m3u8 = self._opener.open(playlist_url).read().decode("utf-8")
        last_url = next(
            (
                line
                for line in reversed(playlist_m3u8.splitlines())
                if re.match("https://", line)
            ),
            None,
        )
        return last_url  # XXX Assuming the last URL is the highest quality
        