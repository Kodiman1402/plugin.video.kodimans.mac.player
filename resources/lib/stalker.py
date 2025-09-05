"""Stalker portal client using only Python's standard library."""

import json
import urllib.parse
import urllib.request


class StalkerClient:
    def __init__(self, portal_url, mac):
        self.portal_url = portal_url.rstrip("/")
        self.mac = mac
        self.token = None
        self.profile = {}
        self.channels = []
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": self.portal_url + "/c/",
            "Cookie": f"mac={self.mac}; stb_lang=en; timezone=Europe/Berlin",
        }

    def call_api(self, endpoint, params=None):
        url = f"{self.portal_url}/portal.php"
        base_params = {
            "type": "stb",
            "action": endpoint,
            "JsHttpRequest": "1-xml",
        }
        if params:
            base_params.update(params)

        headers = self.headers.copy()
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        query = urllib.parse.urlencode(base_params)
        full_url = f"{url}?{query}"
        request = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
        return data.get("js", {})

    def handshake(self):
        data = self.call_api("handshake", {"token": ""})
        self.token = data.get("token")

    def get_profile(self):
        self.profile = self.call_api("get_profile")

    def get_all_channels(self):
        if not self.channels:
            data = self.call_api("get_all_channels")
            self.channels = data.get("data", [])
        return self.channels

    def get_stream_link(self, cmd):
        data = self.call_api("create_link", {"cmd": cmd})
        return data.get("cmd")

    def initialize(self):
        self.handshake()
        self.get_profile()

