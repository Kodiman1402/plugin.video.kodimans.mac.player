import sys
import urllib.parse
import xbmcplugin
import xbmcgui
import xbmcaddon
import os
from collections import defaultdict

sys.path.append(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'lib'))
from stalker import StalkerClient

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])
PARAMS = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

PORTAL = addon.getSetting("portal_url")
MAC = addon.getSetting("mac_address")
client = StalkerClient(PORTAL, MAC)
client.initialize()

def list_categories():
    channels = client.get_all_channels()
    grouped = defaultdict(list)
    for ch in channels:
        genre = ch.get("tv_genre", "Andere")
        grouped[genre].append(ch)

    for genre in sorted(grouped.keys()):
        url = f"{BASE_URL}?action=list&genre={urllib.parse.quote(genre)}"
        li = xbmcgui.ListItem(label=genre)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_channels_by_genre(genre):
    channels = client.get_all_channels()
    for ch in channels:
        if ch.get("tv_genre", "Andere") == genre:
            name = ch.get("name", "Unnamed")
            cmd = ch.get("cmd", "")
            epg = ch.get("now", {}).get("name", "")
            label = f"{name} - {epg}" if epg else name
            url = f"{BASE_URL}?action=play&cmd={urllib.parse.quote(cmd)}"
            li = xbmcgui.ListItem(label=label)
            xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def play_stream():
    cmd = PARAMS.get("cmd", [""])[0]
    stream_url = client.get_stream_link(cmd)
    li = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(HANDLE, True, li)

if __name__ == "__main__":
    action = PARAMS.get("action", [""])[0]
    if action == "play":
        play_stream()
    elif action == "list":
        genre = PARAMS.get("genre", ["Andere"])[0]
        list_channels_by_genre(genre)
    else:
        list_categories()
