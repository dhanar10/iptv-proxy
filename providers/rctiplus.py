import re

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._opener.addheaders = [('Referer', 'https://www.rctiplus.com/')]
        self._channels = {
            "gtv": "https://d322b885qvsbxg.cloudfront.net/GTV2021.m3u8",
            "inews": "https://d2hfpzcndkyscp.cloudfront.net/INEWS_2021.m3u8",
            "mnctv": "https://d33j155pv2xyba.cloudfront.net/MNCTV_2021.m3u8",
            "rcti": "https://d35d0ifx19oopq.cloudfront.net/RCTI_2021.m3u8"

        }

    def get_channel_names(self):
        return self._channels.keys()

    def get_channel_m3u(self, channel_name):
        if not channel_name in self._channels:
            raise Exception("Wrong channel name")
        base_url = self._channels[channel_name].rsplit("/", 1)[0]
        m3u = self._opener.open(self._channels[channel_name]).read().decode(
            "utf-8").splitlines()
        for i in range(len(m3u)):
            if not m3u[i].startswith("#"):
                m3u[i] = base_url + "/" + m3u[i]    # Add base URL
        return "\n".join(m3u)

    def get_kodi_headers_suffix(self):
        return "|referer=https://www.rctiplus.com/"
