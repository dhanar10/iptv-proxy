import unittest
import urllib

from api.useetv import UseeTvApi


class UseeTvApiTests(unittest.TestCase):
    def test_get_channel_list(self):
        api = UseeTvApi()
        self.assertTrue(len(api.get_channel_list()) > 0)

    def test_get_url_channel_valid(self):
        api = UseeTvApi()
        channel = api.get_channel_list()[0]
        self.assertTrue(api.get_url(channel))

    def test_get_url_channel_invalid(self):
        api = UseeTvApi()
        with self.assertRaises(urllib.error.HTTPError):
            api.get_url("null")


if __name__ == "__main__":
    unittest.main()
