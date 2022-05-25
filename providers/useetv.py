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
        html = self._opener.open(
            f"https://www.useetv.com/livetv/{channel_name}").read().decode("utf-8")
        m3u_query = re.search(
            'q[0-9]+ ?= ?("|\')(?P<value>[^\'"]+)("|\')',
            html
        )
        mpd_query = re.search(
            'v[0-9]+ ?= ?("|\')(?P<value>[^\'"]+)("|\')',
            html
        )
        if m3u_query:
            playlist = self._opener.open(b64decode(m3u_query.group("value")).decode(
                "utf-8")).read().decode("utf-8")
        elif mpd_query:
            playlist = (
                '#EXTM3U\n'  '#EXT-X-STREAM-INF:BANDWIDTH=0,RESOLUTION=0x0,NAME="mpd"\n'  f'{mpd_query.group("value")}')
        else:
            raise Exception("Wrong channel name")
        return playlist

    def get_kodi_headers_suffix(self):
        return "|user-agent=Mozilla"
