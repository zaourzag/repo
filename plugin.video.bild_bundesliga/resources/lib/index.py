import sys
import urllib
import os.path
import xbmcgui
import xbmcplugin

URI = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])
PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THUMBNAIL_PATH = os.path.join(PATH, 'media')

def add_dir(title, thumb, arg_dict):
    link = '%s?%s' % (URI, urllib.urlencode(arg_dict))
    if not thumb.startswith('http'):
        thumb = os.path.join(THUMBNAIL_PATH, thumb)
    item = xbmcgui.ListItem(title, thumbnailImage=thumb)
    return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=link, listitem=item, isFolder=True)

def index(arg):
    add_dir('[B]1. Bundesliga[/B]', 'bundesliga.jpg', {'lib':'bundesliga', 'function':'list_matchdays', 'arg':'1'})
    add_dir('[B]2. Bundesliga[/B]', 'bundesliga.jpg', {'lib':'bundesliga', 'function':'list_matchdays', 'arg':'2'})
    add_dir('Neueste Videos', 'bundesliga.jpg', {'lib':'videos', 'function':'list_videos', 'arg':'tb-neueste-37704250--0--1'})
    add_dir('Bundesliga News', 'bundesliga.jpg', {'lib':'videos', 'function':'list_videos', 'arg':'tb-bundesliga-news-37790084--0--8'})
    add_dir('The Voice of Bundesliga', 'bundesliga.jpg', {'lib':'videos', 'function':'list_videos', 'arg':'tb-voice-of-buli-38512690--0--4'})
    add_dir('Pressekonferenzen', 'bundesliga.jpg', {'lib':'videos', 'function':'list_videos', 'arg':'tb-pressekonferenzen-37721734--0--8'})
    add_dir('Tor des Spieltags', 'bundesliga.jpg', {'lib':'videos', 'function':'list_videos', 'arg':'tb-tor-des-spieltages-40007212--0--8'})
    add_dir('Meistgeklickte Videos', 'bundesliga.jpg', {'lib':'videos', 'function':'list_videos', 'arg':'tb-meistgeklickt-37704254--0--2'})
    add_dir('Matze Knop: Knops Kult Liga', 'knop.jpg', {'lib':'videos', 'function':'list_videos', 'arg':'tb-matze-knop-37721724--0--8'})
    xbmcplugin.endOfDirectory(ADDON_HANDLE)