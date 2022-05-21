import re
import time

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, HTTPError
from time import time


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
        self._stream_url_cache = {}

    def get_kodi_url_suffix(self):
        return "|referer=https://www.rctiplus.com/"

    def get_channel_names(self):
        return self._channels.keys()

    def get_stream(self, channel_name):
        c = self._stream_url_cache.get(channel_name)
        if c and int(time()) < c[0]:
            channel_url = c[1]
        else:
            m3u = self._opener.open(self._channels[channel_name]).read().decode("utf-8").splitlines()
            stream_urls = {}
            stream_quality = None
            for line in m3u:
                if line.startswith("#EXT-X-STREAM-INF"):
                    stream_quality = int(
                        re.search('RESOLUTION=[0-9]+x(?P<quality>[0-9]+)', line).group("quality"))
                    continue
                if stream_quality and not line.startswith("#"):
                    base_url = self._channels[channel_name].rsplit("/", 1)[0]
                    stream_urls[stream_quality] = base_url + "/" + line
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
