# -*- coding: utf-8 -*-
import unittest

from user_agent_py.core import parse, USER_AGENT_PY_VERSION


class TestParse(unittest.TestCase):

    def test_version_string(self):
        self.assertIsInstance(USER_AGENT_PY_VERSION, str)
        self.assertTrue(USER_AGENT_PY_VERSION)

    def test_chrome_on_windows(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Chrome")
        self.assertEqual(r["browser"]["version"], "120.0.0.0")
        self.assertEqual(r["engine"]["family"], "Blink")
        self.assertEqual(r["engine"]["version"], "120.0.0.0")
        self.assertEqual(r["operating_system"]["family"], "Windows")
        self.assertEqual(r["operating_system"]["version"], "10/11")
        self.assertEqual(r["device_type"]["family"], "desktop")

    def test_firefox_on_linux(self):
        ua = "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Firefox")
        self.assertEqual(r["browser"]["version"], "121.0")
        self.assertEqual(r["engine"]["family"], "Gecko")
        self.assertEqual(r["operating_system"]["family"], "Linux")
        self.assertEqual(r["operating_system"]["version"], "")
        self.assertEqual(r["device_type"]["family"], "desktop")

    def test_safari_on_macos(self):
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Safari")
        self.assertEqual(r["browser"]["version"], "17.1")
        self.assertEqual(r["engine"]["family"], "WebKit")
        self.assertEqual(r["operating_system"]["family"], "macOS")
        self.assertEqual(r["operating_system"]["version"], "15.7")
        self.assertEqual(r["device_type"]["family"], "desktop")

    def test_safari_on_iphone(self):
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Safari")
        self.assertEqual(r["operating_system"]["family"], "iOS")
        self.assertEqual(r["operating_system"]["version"], "17.1")
        self.assertEqual(r["device_type"]["family"], "mobile")

    def test_edge_on_windows(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Edge")
        self.assertEqual(r["browser"]["version"], "120.0.0.0")
        self.assertEqual(r["operating_system"]["family"], "Windows")
        self.assertEqual(r["device_type"]["family"], "desktop")

    def test_internet_explorer_11(self):
        ua = "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Internet Explorer")
        self.assertEqual(r["browser"]["version"], "11.0")
        self.assertEqual(r["engine"]["family"], "Trident")
        self.assertEqual(r["operating_system"]["family"], "Windows")
        self.assertEqual(r["operating_system"]["version"], "7")

    def test_internet_explorer_legacy(self):
        ua = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Internet Explorer")
        self.assertEqual(r["browser"]["version"], "7.0")
        self.assertEqual(r["operating_system"]["family"], "Windows")
        self.assertEqual(r["operating_system"]["version"], "Vista")

    def test_android_chrome(self):
        ua = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Chrome")
        self.assertEqual(r["browser"]["version"], "120.0.0.0")
        self.assertEqual(r["engine"]["family"], "Blink")
        self.assertEqual(r["operating_system"]["family"], "Android")
        self.assertEqual(r["operating_system"]["version"], "13")
        self.assertEqual(r["device_type"]["family"], "mobile")

    def test_ipad_tablet(self):
        ua = "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        r = parse(ua)
        self.assertEqual(r["device_type"]["family"], "tablet")
        self.assertEqual(r["operating_system"]["family"], "iOS")
        self.assertEqual(r["operating_system"]["version"], "16.0")

    def test_googlebot(self):
        ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        r = parse(ua)
        self.assertEqual(r["device_type"]["family"], "bot")

    def test_empty_string(self):
        r = parse("")
        self.assertEqual(r["browser"]["family"], "")
        self.assertEqual(r["engine"]["family"], "")
        self.assertEqual(r["operating_system"]["family"], "")
        self.assertEqual(r["device_type"]["family"], "other")
        self.assertEqual(r["browser"]["version"], "")

    def test_whitespace_string(self):
        r = parse("   ")
        self.assertEqual(r["device_type"]["family"], "other")

    def test_unrecognized_string(self):
        ua = "curl/7.81.0"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "")
        self.assertEqual(r["engine"]["family"], "")
        self.assertEqual(r["operating_system"]["family"], "")
        self.assertEqual(r["device_type"]["family"], "other")

    def test_returns_consistent_shape(self):
        r = parse("curl/7.81.0")
        self.assertIn("browser", r)
        self.assertIn("engine", r)
        self.assertIn("operating_system", r)
        self.assertIn("device_type", r)
        for key in ("browser", "engine", "operating_system", "device_type"):
            self.assertIn("family", r[key])
            self.assertIn("version", r[key])
            self.assertIsInstance(r[key]["family"], str)
            self.assertIsInstance(r[key]["version"], str)

    def test_type_error_on_non_string(self):
        with self.assertRaises(TypeError):
            parse(None)
        with self.assertRaises(TypeError):
            parse(123)

    def test_opera(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0"
        r = parse(ua)
        self.assertEqual(r["browser"]["family"], "Opera")
        self.assertEqual(r["browser"]["version"], "106.0.0.0")

    def test_chromeos(self):
        ua = "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        r = parse(ua)
        self.assertEqual(r["operating_system"]["family"], "Chrome OS")
        self.assertEqual(r["device_type"]["family"], "desktop")


if __name__ == "__main__":
    unittest.main()
