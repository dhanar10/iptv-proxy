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
        channel_names = IptvProxyTests.Providers['useetv'].get_channel_names()
        #print(channel_names)
        self.assertTrue("useeprime" in channel_names)

    def  test_useetv_get_stream_valid(self):
        url = IptvProxyTests.Providers['useetv'].get_stream("useeprime")
        #print(url)
        self.assertTrue(url)

    def test_useetv_get_stream_invalid(self):
        with self.assertRaises(urllib.error.HTTPError):
            IptvProxyTests.Providers['useetv'].get_stream("invalid")

    def test_rctiplus_get_channel_names(self):
        channel_names = IptvProxyTests.Providers['rctiplus'].get_channel_names()
        #print(channel_names)
        self.assertTrue("gtv" in channel_names)

    def  test_rctiplus_get_stream_valid(self):
        url = IptvProxyTests.Providers['rctiplus'].get_stream("gtv")
        #print(url)
        self.assertTrue(url)

    # def test_rctiplus_get_stream_invalid(self):
    #     with self.assertRaises(urllib.error.HTTPError):
    #         IptvProxyTests.Providers['rctiplus'].get_stream("invalid")


if __name__ == "__main__":
    unittest.main()
