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

    def get_channel_playlist(self, channel_name):
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
            "utf-8")).read().decode("utf-8")
        return m3u

    def get_kodi_headers_suffix(self):
        return "|user-agent=Mozilla"
