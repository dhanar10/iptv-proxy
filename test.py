import unittest
import urllib

from api.useetv import UseeTvApi


class UseeTvApiTests(unittest.TestCase):
    def test_get_channel_list(self):
        api = UseeTvApi()
        channel_list = api.get_channel_list()
        #print(channel_list)
        self.assertTrue("tvri" in channel_list)

    def test_get_url_channel_valid(self):
        api = UseeTvApi()
        url = api.get_url("tvri")
        #print(url)
        self.assertTrue(url)

    def test_get_url_channel_invalid(self):
        api = UseeTvApi()
        with self.assertRaises(urllib.error.HTTPError):
            api.get_url("invalid")


if __name__ == "__main__":
    unittest.main()
