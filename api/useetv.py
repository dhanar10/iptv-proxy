import re
import time

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, HTTPError
from time import time


class UseeTvApi:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._cache = {}

    def get_channel_list(self):
        q = re.findall(
            'https://www.useetv.com/pimages/logo_([a-z0-9]+)_small1.png',
            (
                self._opener.open(f"https://www.useetv.com/tv/live")
                .read()
                .decode("utf-8")
            ),
        )
        if not q:
            raise HTTPError(404)
        return q

    def get_url(self, channel):
        c = self._cache.get(channel)
        if c and int(time()) < c[0]:
            url = c[1]
        else:
            q = re.search(
                'q[0-9]+ ?= ?"(?P<value>[^"]+)"',
                (
                    self._opener.open(f"https://www.useetv.com/livetv/{channel}")
                    .read()
                    .decode("utf-8")
                ),
            )
            if not q:
                raise HTTPError(404)
            url = next(
                (
                    line
                    for line in reversed(
                        self._opener.open(b64decode(q.group("value")).decode("utf-8"))
                        .read()
                        .decode("utf-8")
                        .splitlines()
                    )
                    if re.match("https://", line)
                ),
                None,
            )  # XXX Assuming the last URL is the highest quality
            if not url:
                raise HTTPError(404)
            self._cache[channel] = (int(time()) + 300, url)  # XXX Cache 5 minutes
        return url
