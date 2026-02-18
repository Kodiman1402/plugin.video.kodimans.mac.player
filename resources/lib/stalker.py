"""Stalker portal client using only Python's standard library."""

import json
import urllib.parse
import urllib.request
import urllib.error

class StalkerClient:
    def __init__(self, portal_url, mac):
        self.portal_url = portal_url.rstrip("/")
        # URL Korrektur falls User /c/ vergessen hat aber benötigt wird, 
        # oder falls portal.php direkt angesprochen werden muss.
        self.mac = mac
        self.token = None
        self.profile = {}
        self.channels = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
            "Referer": self.portal_url + "/",
            "Cookie": f"mac={self.mac}; stb_lang=en; timezone=Europe/Berlin",
        }

    def call_api(self, endpoint, params=None):
        # Aufbau der URL: Stalker nutzt meist /portal.php
        if "portal.php" in self.portal_url:
            base_url = self.portal_url
        else:
            base_url = f"{self.portal_url}/portal.php"

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
        full_url = f"{base_url}?{query}"
        
        try:
            request = urllib.request.Request(full_url, headers=headers)
            # Timeout wichtig, damit Kodi nicht hängt
            with urllib.request.urlopen(request, timeout=10) as response:
                content = response.read()
                try:
                    # Stalker API gibt manchmal Text/HTML bei Fehlern zurück
                    data = json.loads(content)
                    return data.get("js", {})
                except json.JSONDecodeError:
                    return {}
        except (urllib.error.URLError, urllib.error.HTTPError):
            # Verbindungsprobleme still abfangen oder loggen
            return {}
        except Exception:
            return {}

    def handshake(self):
        # Token holen
        data = self.call_api("handshake", {"token": ""})
        if data:
            self.token = data.get("token")

    def get_profile(self):
        self.profile = self.call_api("get_profile")

    def get_all_channels(self):
        if not self.channels:
            data = self.call_api("get_all_channels")
            if data:
                self.channels = data.get("data", [])
        return self.channels

    def get_stream_link(self, cmd):
        data = self.call_api("create_link", {"cmd": cmd})
        if not data:
            return ""
        # Manchmal ist der Link in 'cmd', manchmal in 'url'
        return data.get("cmd") or data.get("url") or ""

    def initialize(self):
        self.handshake()
        # Profil laden ist optional, aber gut zum Testen der Verbindung
        if self.token:
            self.get_profile()

