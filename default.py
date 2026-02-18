import sys
import os
import urllib.parse
import xbmcplugin
import xbmcgui
import xbmcaddon
from collections import defaultdict

# Sicherstellen, dass Python die lokalen Module im 'resources/lib' Ordner findet
addon_dir = xbmcaddon.Addon().getAddonInfo('path')
lib_dir = os.path.join(addon_dir, 'resources', 'lib')
sys.path.append(lib_dir)

from stalker import StalkerClient

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])
try:
    PARAMS = urllib.parse.parse_qs(sys.argv[2][1:])
except IndexError:
    PARAMS = {}

addon = xbmcaddon.Addon()
PORTAL = addon.getSetting("portal_url")
MAC = addon.getSetting("mac_address")

def list_categories():
    xbmcplugin.setContent(HANDLE, 'videos')
    
    # Check ob Einstellungen leer sind
    if not PORTAL or not MAC or "00:1A:79" in MAC: # Standard MAC Check
        li = xbmcgui.ListItem(label="[COLOR red]Bitte Einstellungen konfigurieren![/COLOR]")
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=BASE_URL, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(HANDLE)
        xbmcaddon.Addon().openSettings()
        return

    try:
        client = StalkerClient(PORTAL, MAC)
        client.initialize()
        channels = client.get_all_channels()
    except Exception as e:
        xbmcgui.Dialog().notification("Fehler", f"Verbindung fehlgeschlagen: {str(e)}", xbmcgui.NOTIFICATION_ERROR)
        return

    if not channels:
        xbmcgui.Dialog().notification("Info", "Keine Kanäle gefunden. MAC prüfen.", xbmcgui.NOTIFICATION_WARNING)
        return

    grouped = defaultdict(list)
    for ch in channels:
        genre = ch.get("tv_genre", "Andere")
        grouped[genre].append(ch)

    for genre in sorted(grouped.keys()):
        url = f"{BASE_URL}?action=list&genre={urllib.parse.quote(genre)}"
        li = xbmcgui.ListItem(label=genre)
        # Standard Ordner Icon setzen
        li.setArt({'icon': 'DefaultFolder.png'})
        xbmcplugin.addDirectoryItem(
            handle=HANDLE,
            url=url,
            listitem=li,
            isFolder=True,
        )
    xbmcplugin.endOfDirectory(HANDLE)


def list_channels_by_genre(genre):
    xbmcplugin.setContent(HANDLE, 'videos')
    try:
        client = StalkerClient(PORTAL, MAC)
        client.initialize()
        channels = client.get_all_channels()
    except Exception:
        return

    for ch in channels:
        if ch.get("tv_genre", "Andere") == genre:
            name = ch.get("name", "Unnamed")
            cmd = ch.get("cmd", "")
            epg = ch.get("now", {}).get("name", "")
            logo = ch.get("logo", "")
            
            # Label Formatierung
            label = name
            if epg:
                label += f" - [COLOR gray]{epg}[/COLOR]"
            
            url = f"{BASE_URL}?action=play&cmd={urllib.parse.quote(cmd)}"
            li = xbmcgui.ListItem(label=label)
            
            # Metadaten setzen für bessere Ansicht
            li.setInfo('video', {'title': name, 'plot': epg})
            if logo:
                li.setArt({'thumb': logo, 'icon': logo})
            
            li.setIsPlayable(True)
            xbmcplugin.addDirectoryItem(
                handle=HANDLE,
                url=url,
                listitem=li,
                isFolder=False,
            )
    xbmcplugin.endOfDirectory(HANDLE)


def play_stream():
    cmd = PARAMS.get("cmd", [""])[0]
    if not cmd:
        return

    try:
        client = StalkerClient(PORTAL, MAC)
        client.initialize()
        stream_url = client.get_stream_link(cmd)
        
        if not stream_url:
            xbmcgui.Dialog().notification("Fehler", "Kein Stream-Link erhalten", xbmcgui.NOTIFICATION_ERROR)
            return

        # Einfache Prüfung ob es ein ffmpeg link ist (passiert manchmal bei Stalker)
        if " " in stream_url and "http" not in stream_url.split(" ")[0]:
             # Fallback logic falls nötig, hier nehmen wir an es ist eine URL
             pass
        
        # User-Agent für den Player setzen (Wichtig für viele IPTV Anbieter)
        # Kodi Syntax: url|User-Agent=...
        if "|" not in stream_url:
            stream_url += "|User-Agent=Mozilla/5.0"

        li = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(HANDLE, True, li)
        
    except Exception as e:
        xbmcgui.Dialog().notification("Fehler", "Abspielen fehlgeschlagen", xbmcgui.NOTIFICATION_ERROR)


if __name__ == "__main__":
    action = PARAMS.get("action", [""])[0]
    if action == "play":
        play_stream()
    elif action == "list":
        genre = PARAMS.get("genre", ["Andere"])[0]
        list_channels_by_genre(genre)
    else:
        list_categories()
