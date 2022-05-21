from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._opener.addheaders = [('Referer', 'https://www.rctiplus.com/')]
        self._channels = {
            "cna": "https://d2e1asnsl7br7b.cloudfront.net/7782e205e72f43aeb4a48ec97f66ebbe/index.m3u8"
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
        return ""
