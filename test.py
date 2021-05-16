import unittest
import urllib

from api.useetv import UseeTvApi


class UseeTvApiTests(unittest.TestCase):
    def test_get_url_channel_valid(self):
        api = UseeTvApi()
        self.assertTrue(api.get_url("tvri"))

    def test_get_url_channel_invalid(self):
        api = UseeTvApi()
        with self.assertRaises(urllib.error.HTTPError):
            api.get_url("null")


if __name__ == "__main__":
    unittest.main()
