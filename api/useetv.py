import re

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, HTTPError


class UseeTvApi:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def get_url(self, channel):
        q = re.search(
            'q[0-9]+="(?P<value>[^"]+)"',
            (
                self._opener.open(f"https://www.useetv.com/livetv/{channel}")
                .read()
                .decode("utf-8")
            ),
        )
        if q:
            playlist_url = b64decode(q.group('value')).decode("utf-8")
            last_url = next(
                (
                    line
                    for line in reversed(
                        self._opener.open(playlist_url)
                        .read()
                        .decode("utf-8")
                        .splitlines()
                    )
                    if re.match("https://", line)
                ),
                None,
            )  # XXX Assuming the last URL is the highest quality
        if not last_url:
            raise HTTPError(404)
        return last_url
