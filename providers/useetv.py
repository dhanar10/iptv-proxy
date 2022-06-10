import re

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor
from time import time


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._channel_name_override = {
            "ruangtrampil": "useeinfo"
        }
        self._mpd_channels = [
            "useeinfo",
            "useephoto",
            "tvri",
            "beritasatu",
            "prambors",
            "indikids",
        ]
        self._mpd_url_cache = {}

    def get_channel_names(self):
        channel_names = re.findall(
            "https://images.useetv.com/logo_([a-z0-9]+)_[a-z0-9]+.png",
            (
                self._opener.open("https://www.useetv.com/tv/live")
                .read()
                .decode("utf-8")
            ),
        )
        if not channel_names:
            raise Exception("Failed to get channel names")
        for k, v in self._channel_name_override.items():
            channel_names[channel_names.index(k)] = v
        return list(set(channel_names) - set(self._mpd_channels))

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
            mpd_url_cache = self._mpd_url_cache.get(channel_name)
            if mpd_url_cache and int(time()) < mpd_url_cache[1]:
                mpd_url = mpd_url_cache[0]
            else:
                mpd_url = mpd_query.group("value")
            self._mpd_url_cache[channel_name] = (
                mpd_url, int(time()) + 300)  # Cache for 5 minutes
            baseUrl = mpd_url.split(
                "?")[0].rsplit("/", 1)[0] + "/"
            playlist = self._opener.open(mpd_url).read().decode("utf-8")
            # Kodi inpustream MPD does not support BaseURL?
            playlist = playlist.replace(' media="', f' media="{baseUrl}').replace(
                ' initialization="', f' initialization="{baseUrl}')
        else:
            raise Exception("Wrong channel name")
        return playlist

    def get_kodi_props(self, channel_name):
        if channel_name in self._mpd_channels:
            return (
                "#KODIPROP:inputstream=inputstream.adaptive\n"
                "#KODIPROP:inputstream.adaptive.manifest_type=mpd\n"
            )
        else:
            return ""

    def get_kodi_url_suffix(self):
        return "|user-agent=Mozilla"
