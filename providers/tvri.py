from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._channels = {
            "tvriworld": "http://118.97.50.107/Content/HLS/Live/Channel(TVRI3)/index.m3u8",
            "tvrijakarta": "http://118.97.50.107/Content/HLS/Live/Channel(TVRIDKI)/index.m3u8",
            "tvrijawatengah": "http://118.97.50.107/Content/HLS/Live/Channel(TVRIJATENGSEMARANG)/index.m3u8",
            "tvriyogyakarta": "http://118.97.50.107/Content/HLS/Live/Channel(TVRIYOGYAKARTA)/index.m3u8"
        }

    def get_channel_names(self):
        return self._channels.keys()

    def get_channel_playlist(self, channel_name):
        if not channel_name in self._channels:
            raise Exception("Wrong channel name")
        base_url = self._channels[channel_name].rsplit("/", 1)[0]
        m3u = self._opener.open(self._channels[channel_name]).read().decode(
            "utf-8").splitlines()
        for i in range(len(m3u)):
            if not m3u[i].startswith("#"):
                m3u[i] = base_url + "/" + m3u[i]    # Add base URL
        return "\n".join(m3u)

    def get_kodi_props(self, channel_name):
        return ""

    def get_kodi_url_suffix(self):
        return ""
