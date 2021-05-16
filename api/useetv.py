import re

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, HTTPError


class UseeTvApi:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def get_channel_list(self):
        return [
            "seatoday",
            "tvri",
            "kompastv",
            "metrotv",
            "net",
            "rtv",
            "antara",
            "balitv",
            "beritasatu",
            "dwtv",
            "french24",
            "jaktv",
            "jtv",
            "muitv",
            "trans7",
            "transtv",
            "tvedukasi",
            "tv9",
            "arirang",
            "alquran",
            "tawaftv",
            "mqtv",
            "mtatv",
            "muhammadiyahtv",
            "rodjatv",
            "chinesedrama",
            "daaitv",
            "nusantaratv",
            "inews",
            "mykids",
            "nhkworld",
            "mncnews",
            "mykids",
            "outdoor",
        ]  # TODO Scrape html

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
            playlist_url = b64decode(q.group("value")).decode("utf-8")
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
