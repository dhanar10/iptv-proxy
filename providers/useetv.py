import re
import xml.etree.ElementTree as ET

from base64 import b64decode
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor
from time import time


class Provider:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self._opener.addheaders = [('User-Agent', 'Mozilla')]
        self._channel_name_override = {
            "ruangtrampil": "useeinfo"
        }
        self._mpd_channels = [
            "useeinfo",
            "useephoto",
            "tvri",
            "beritasatu",
            "pramborstv",
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
        # return list(set(channel_names) - set(self._mpd_channels))
        return channel_names

    def get_channel_playlist(self, channel_name):
        url = None
        if channel_name in self._mpd_url_cache:
            mpd_url_cache_value = self._mpd_url_cache.get(channel_name)
            if mpd_url_cache_value and int(time()) < mpd_url_cache_value[0]:
                url = mpd_url_cache_value[1]
        if not url:
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
        else:
            m3u_query = False
            mpd_query = True
        if m3u_query:
            playlist = self._opener.open(b64decode(m3u_query.group("value")).decode(
                "utf-8")).read().decode("utf-8")
        elif mpd_query:
            if not url:
                url = mpd_query.group("value")
                self._mpd_url_cache[channel_name] = (int(time()) + 300, url)
            mpd_xml = self._opener.open(url).read()
            mpd_xml_ns = "urn:mpeg:dash:schema:mpd:2011"
            ET.register_namespace("", mpd_xml_ns)
            mpd_root = ET.fromstring(mpd_xml)
            base_url = url.split("?")[0].rsplit("/", 1)[0] + "/"
            for mpd_adaptationset in mpd_root.iterfind(f".//{{{mpd_xml_ns}}}AdaptationSet"):
                 for mpd_representation in mpd_adaptationset.findall(f"{{{mpd_xml_ns}}}Representation"):
                    if mpd_representation.get("mimeType") == "video/mp4" and (not mpd_representation.get("height") in ("480", "540")):    # FIXME
                            mpd_adaptationset.remove(mpd_representation)
            for mpd_segmenttemplate in mpd_root.iterfind(f".//{{{mpd_xml_ns}}}Representation[@mimeType='video/mp4']/{{{mpd_xml_ns}}}SegmentTemplate"):
                mpd_segmenttemplate.set("initialization", base_url + "/" + mpd_segmenttemplate.get("initialization"))
                mpd_segmenttemplate.set("media", f"{channel_name}/video/$Time$")
            for mpd_segmenttemplate in mpd_root.iterfind(f".//{{{mpd_xml_ns}}}Representation[@mimeType='audio/mp4']/{{{mpd_xml_ns}}}SegmentTemplate"):
                mpd_segmenttemplate.set("initialization", base_url + "/" + mpd_segmenttemplate.get("initialization"))
                mpd_segmenttemplate.set("media", f"{channel_name}/audio/$Time$")
            playlist = ET.tostring(
                mpd_root, encoding='utf-8').decode('utf-8')
            #print(playlist)
        else:
            raise Exception("Wrong channel name")
        return playlist

    def get_channel_segment(self, channel_name, type, time):
        mpd_url_cache_value = self._mpd_url_cache.get(channel_name)
        url = mpd_url_cache_value[1]
        mpd_xml = self._opener.open(url).read()
        mpd_xml_ns = "urn:mpeg:dash:schema:mpd:2011"
        ET.register_namespace("", mpd_xml_ns)
        mpd_root = ET.fromstring(mpd_xml)
        base_url = url.split("?")[0].rsplit("/", 1)[0] + "/"
        for mpd_adaptationset in mpd_root.iterfind(f".//{{{mpd_xml_ns}}}AdaptationSet"):
            for mpd_representation in mpd_adaptationset.findall(f"{{{mpd_xml_ns}}}Representation"):
                if mpd_representation.get("mimeType") == "video/mp4" and (not mpd_representation.get("height") in ("480", "540")):    # FIXME
                        mpd_adaptationset.remove(mpd_representation)
        for mpd_segmenttemplate in mpd_root.iterfind(f".//{{{mpd_xml_ns}}}Representation[@mimeType='{type}/mp4']/{{{mpd_xml_ns}}}SegmentTemplate"):
            for mpd_s in mpd_segmenttemplate.iterfind(f"{{{mpd_xml_ns}}}SegmentTimeline/{{{mpd_xml_ns}}}S"):
                if int(mpd_s.get('t')) >= int(time):
                    #print(base_url + mpd_segmenttemplate.get("media").replace("$Time$", mpd_s.get('t')))
                    segment = self._opener.open(base_url + mpd_segmenttemplate.get("media").replace("$Time$", mpd_s.get('t'))).read()
                    return segment

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
