from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._channels = {
            "duniagames": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(ec41a5e2-09e4-431d-b92e-383fa7abe25c)/index.m3u8",
            "egg": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(cbd08544-cbff-407c-9a6e-833494cb8bad)/index.m3u8",
            "ftv": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(5cd2bf10-1ac0-4fa7-9543-3520f01b3378)/index.m3u8",
            "indonesia": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(20baf7aa-fd51-480f-87b3-dc4198090e86)/index.m3u8",
            "mcc": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(9430f215-8ccb-4322-affd-6dbc97e259bd)/index.m3u8",
            "rockentertainment": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(7110fb03-7887-4104-a6cd-0ba950b28ea4)/index.m3u8",
            "rockextreme": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(0c72959b-2ccf-443c-a664-66170e390be1)/index.m3u8",
            "ruangtrampil": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(2b945e2e-4297-4be9-9a45-aa023c890e13)/index.m3u8",
            "useephoto": "https://cdn-telkomsel-01.akamaized.net/Content/HLS/Live/channel(f1b6e507-d639-4d66-858a-e457d55ddbb2)/index.m3u8"
        }

    def get_channel_names(self):
        return self._channels.keys()

    def get_channel_playlist(self, channel_name):
        if not channel_name in self._channels:
            raise Exception(f"Wrong channel name: {channel_name}")
        base_url = self._channels[channel_name].rsplit("/", 1)[0]
        m3u = self._opener.open(self._channels[channel_name]).read().decode(
            "utf-8").splitlines()
        for i in range(len(m3u)):
            if  m3u[i].startswith("#EXT-X-MEDIA:TYPE=AUDIO"):
                m3u[i] = m3u[i].replace(',URI="',f',URI="{base_url}/')
            if not m3u[i].startswith("#"):
                m3u[i] = base_url + "/" + m3u[i]    # Add base URL
        return "\n".join(m3u)

    def get_kodi_props(self, channel_name):
        return ""

    def get_kodi_url_suffix(self):
        return ""
