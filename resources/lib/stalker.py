import requests
import time
import json
import hashlib
import random

class StalkerClient:
    def __init__(self, portal_url, mac):
        self.portal_url = portal_url.rstrip("/")
        self.mac = mac
        self.token = None
        self.profile = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": self.portal_url + "/c/",
            "Cookie": f"mac={self.mac}; stb_lang=en; timezone=Europe/Berlin"
        }
        self.session = requests.Session()

    def call_api(self, endpoint, params=None):
        url = f"{self.portal_url}/portal.php"
        base_params = {
            "type": "stb",
            "action": endpoint,
            "JsHttpRequest": "1-xml"
        }
        if params:
            base_params.update(params)

        headers = self.headers.copy()
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = self.session.get(url, params=base_params, headers=headers, timeout=10)
        data = response.json()
        return data.get("js", {})

    def handshake(self):
        data = self.call_api("handshake", {"token": ""})
        self.token = data.get("token")

    def get_profile(self):
        self.profile = self.call_api("get_profile")

    def get_all_channels(self):
        return self.call_api("get_all_channels")

    def get_stream_link(self, cmd):
        data = self.call_api("create_link", {"cmd": cmd})
        return data.get("cmd")

    def initialize(self):
        self.handshake()
        self.get_profile()
