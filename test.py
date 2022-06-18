import importlib
import pkgutil
import unittest

test_provider_channel_name_list = [
    ('biznet', 'biznetkids'),
    ('cna', 'cna'),
    ('cnbc', 'cnbcindonesia'),
    #('maxstream', 'mcc'),
    ('rctiplus', 'gtv'),
    ('spacetoon', 'spacetoon'),
    ('tvri', 'tvri'),
    ('useetv', 'useeprime'),    # m3u
    ('useetv', 'useeinfo')      # mpd
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
            print(playlist)

    def test_get_channel_playlist_invalid(self):
        provider_name_list = [p for p, _ in test_provider_channel_name_list]
        for provider_name in provider_name_list:
            with self.assertRaises(Exception):
                IptvProxyTests.Providers[provider_name].get_channel_playlist(
                    "invalid")


if __name__ == "__main__":
    unittest.main()
