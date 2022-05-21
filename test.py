import importlib
import pkgutil
import unittest
import urllib


class IptvProxyTests(unittest.TestCase):
    def setUp(self):
        IptvProxyTests.Providers = {
            name : importlib.import_module("providers." + name).Provider()
            for finder, name, ispkg
            in pkgutil.iter_modules(path=["providers"])
        }

    def test_useetv_get_channel_names(self):
        channel_list = IptvProxyTests.Providers['useetv'].get_channel_names()
        #print(channel_list)
        self.assertTrue("useeprime" in channel_list)

    def  test_useetv_get_stream_valid(self):
        url = IptvProxyTests.Providers['useetv'].get_stream("useeprime")
        #print(url)
        self.assertTrue(url)

    def test_useetv_get_stream_invalid(self):
        with self.assertRaises(urllib.error.HTTPError):
            IptvProxyTests.Providers['useetv'].get_stream("invalid")


if __name__ == "__main__":
    unittest.main()
