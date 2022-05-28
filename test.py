import importlib
import pkgutil
import unittest

test_provider_channel_name_list = [
    ('biznet', 'biznetkids'),
    ('cna', 'cna'),
    ('rctiplus', 'gtv'),
    ('spacetoon', 'spacetoon'),
    ('useetv', 'useeprime'),    # m3u
    ('useetv', 'tvri')          # mpd
]


class IptvProxyTests(unittest.TestCase):
    def setUp(self):
        IptvProxyTests.Providers = {
            name: importlib.import_module("providers." + name).Provider()
            for finder, name, ispkg
            in pkgutil.iter_modules(path=["providers"])
        }

    def test_get_channel_names(self):
        for provider_name, channel_name in test_provider_channel_name_list:
            print("# " + provider_name)
            channel_names = IptvProxyTests.Providers[provider_name].get_channel_names(
            )
            self.assertTrue(channel_name in channel_names)
            print(channel_names)

    def test_get_channel_playlist_valid(self):
        for provider_name, channel_name in test_provider_channel_name_list:
            print("# " + provider_name)
            playlist = IptvProxyTests.Providers[provider_name].get_channel_playlist(
                channel_name)
            self.assertTrue(playlist)
            if playlist.startswith(str("<MPD")):
                 self.assertTrue("<BaseUrl>" in playlist)
            else:
                self.assertTrue("#EXTM3U" in playlist)
            print(playlist)

    def test_get_channel_playlist_invalid(self):
        provider_name_list = [p for p, _ in test_provider_channel_name_list]
        for provider_name in provider_name_list:
            with self.assertRaises(Exception):
                IptvProxyTests.Providers[provider_name].get_channel_playlist(
                    "invalid")


if __name__ == "__main__":
    unittest.main()
