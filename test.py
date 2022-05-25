import importlib
import pkgutil
import unittest

test_provider_channel_name_list = [
    ('cna', 'cna'), ('rctiplus', 'gtv'), ('useetv', 'useeprime')]


class IptvProxyTests(unittest.TestCase):
    def setUp(self):
        IptvProxyTests.Providers = {
            name: importlib.import_module("providers." + name).Provider()
            for finder, name, ispkg
            in pkgutil.iter_modules(path=["providers"])
        }

    def test_get_channel_names(self):
        for provider_name, channel_name in test_provider_channel_name_list:
            channel_names = IptvProxyTests.Providers[provider_name].get_channel_names(
            )
            self.assertTrue(channel_name in channel_names)

    def test_get_channel_playlist_valid(self):
        for provider_name, channel_name in test_provider_channel_name_list:
            playlist = IptvProxyTests.Providers[provider_name].get_channel_playlist(
                channel_name)
            self.assertTrue(playlist)

    def test_get_channel_playlist_invalid(self):
        for provider_name, channel_name in test_provider_channel_name_list:
            with self.assertRaises(Exception):
                IptvProxyTests.Providers[provider_name].get_channel_playlist(
                    "invalid")


if __name__ == "__main__":
    unittest.main()
