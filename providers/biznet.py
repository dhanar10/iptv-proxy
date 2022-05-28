from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._channels = {
            "biznetadventure": "http://livestream.biznetvideo.net/biznet_adventure/smil:adventure.smil/playlist.m3u8?bizkeyliveCustomParameter=myParameter&bizkeyliveendtime=0&bizkeylivehash=iJYiwvsAhKLgYjtMcoxVp1GZg1XW_wNcrvg-lcNq6Vdy&bizkeylivestarttime=0",
            "biznetlifestyle": "http://livestream.biznetvideo.net/biznet_lifestyle/smil:lifestyle.smil/playlist.m3u8?bizkeyliveCustomParameter=myParameter&bizkeyliveendtime=0&bizkeylivehash=jgDKPclcGdZfvrIDxfMdpT7v_srMWCbubntGo9cCYWpcBBQalMlLQxHswm43PbVR&bizkeylivestarttime=0",
            "biznetkids": "http://livestream.biznetvideo.net/biznet_kids/smil:kids.smil/playlist.m3u8?bizkeyliveCustomParameter=myParameter&bizkeyliveendtime=0&bizkeylivehash=qAri1M2xu_MAlnHwVRtOs24lR8Y_HSDijN2CRNghifUllhYqQSDlkd0qE8CkZwxC&bizkeylivestarttime=0"
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
