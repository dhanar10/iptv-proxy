import importlib
import pkgutil
import unittest


class IptvProxyTests(unittest.TestCase):
    def setUp(self):
        IptvProxyTests.Providers = {
            name: importlib.import_module("providers." + name).Provider()
            for finder, name, ispkg
            in pkgutil.iter_modules(path=["providers"])
        }

    def test_useetv_get_channel_names(self):
        channel_names = IptvProxyTests.Providers['useetv'].get_channel_names()
        self.assertTrue("useeprime" in channel_names)

    def test_useetv_get_channel_m3u_valid(self):
        m3u = IptvProxyTests.Providers['useetv'].get_channel_m3u("useeprime")
        self.assertTrue(m3u)

    def test_useetv_get_channel_m3u_invalid(self):
        with self.assertRaises(Exception):
            IptvProxyTests.Providers['useetv'].get_channel_m3u("invalid")

    def test_rctiplus_get_channel_names(self):
        channel_names = IptvProxyTests.Providers['rctiplus'].get_channel_names(
        )
        self.assertTrue("gtv" in channel_names)

    def test_rctiplus_get_channel_m3u_valid(self):
        m3u = IptvProxyTests.Providers['rctiplus'].get_channel_m3u("gtv")
        self.assertTrue(m3u)

    def test_rctiplus_get_channel_m3u_invalid(self):
        with self.assertRaises(Exception):
            IptvProxyTests.Providers['rctiplus'].get_channel_m3u("invalid")


if __name__ == "__main__":
    unittest.main()
