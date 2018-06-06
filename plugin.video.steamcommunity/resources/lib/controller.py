# -*- coding: utf-8 -*-
# Steam Community
# Copyright (C) 2018 MrKrabat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import json
import inputstreamhelper
from bs4 import BeautifulSoup
from os.path import join
from distutils.version import StrictVersion
try:
    from urllib import URLopener
except ImportError:
    from urllib.request import URLopener

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

from . import api
from . import view


def viewScreenshots(args):
    """Show all screenshots
    """
    # get website
    html = api.getPage(args, "https://steamcommunity.com/apps/allcontenthome/?l=" + args._lang + "&browsefilter=trend&appHubSubSection=2&forceanon=1")
    if not html:
        view.add_item(args, {"title": args._addon.getLocalizedString(30061)})
        view.endofdirectory()
        return

    # parse html
    xbmcplugin.setContent(int(sys.argv[1]), "images")
    soup = BeautifulSoup(html, "html.parser")

    # for every list entry
    for div in soup.find_all("div", {"class": "modalContentLink"}):
        # get values
        sText  = div.find("div", {"class": "apphub_CardContentTitle"}).string.strip()
        sGame = div.find("div", {"class": "apphub_CardContentType"}).string.strip()
        sRating = div.find("div", {"class": "apphub_CardRating"}).string.strip()
        sThumb  = div.find("img", {"class": "apphub_CardContentPreviewImage"})["src"]
        sURL = re.findall(r", (.*?) ", div.find("img", {"class": "apphub_CardContentPreviewImage"})["srcset"])[-1]
        try:
            sAuthor = div.find("div", {"class": "apphub_CardContentAuthorName"}).a.string.strip()
        except AttributeError:
            sAuthor = div.find("div", {"class": "apphub_CardContentAppName"}).a.string.strip()

        # add to view
        view.add_item(args,
                      {"url":         sURL,
                       "mode":        "imageplay",
                       "title":       sAuthor + " - " + sText,
                       "tvshowtitle": sAuthor + " - " + sText,
                       "plot":        sAuthor + "\n" + sText + "\n" + sGame + "\nLikes " + sRating,
                       "plotoutline": sAuthor + "\n" + sText + "\n" + sGame + "\nLikes " + sRating,
                       "thumb":       sThumb,
                       "fanart":      sThumb,
                       "credits":     sAuthor},
                      isFolder=False, mediatype="video")

    view.endofdirectory()


def viewArtwork(args):
    """Show all artwork
    """
    # get website
    html = api.getPage(args, "https://steamcommunity.com/apps/allcontenthome/?l=" + args._lang + "&browsefilter=trend&appHubSubSection=4&forceanon=1")
    if not html:
        view.add_item(args, {"title": args._addon.getLocalizedString(30061)})
        view.endofdirectory()
        return

    # parse html
    xbmcplugin.setContent(int(sys.argv[1]), "images")
    soup = BeautifulSoup(html, "html.parser")

    # for every list entry
    for div in soup.find_all("div", {"class": "modalContentLink"}):
        # get values
        sText  = div.find("div", {"class": "apphub_CardContentTitle"}).string.strip()
        sGame = div.find("div", {"class": "apphub_CardContentType"}).string.strip()
        sRating = div.find("div", {"class": "apphub_CardRating"}).string.strip()
        sThumb  = div.find("img", {"class": "apphub_CardContentPreviewImage"})["src"]
        sURL = re.findall(r", (.*?) ", div.find("img", {"class": "apphub_CardContentPreviewImage"})["srcset"])[-1]
        try:
            sAuthor = div.find("div", {"class": "apphub_CardContentAuthorName"}).a.string.strip()
        except AttributeError:
            sAuthor = div.find("div", {"class": "apphub_CardContentAppName"}).a.string.strip()

        # add to view
        view.add_item(args,
                      {"url":         sURL,
                       "mode":        "imageplay",
                       "title":       sAuthor + " - " + sText,
                       "tvshowtitle": sAuthor + " - " + sText,
                       "plot":        sAuthor + "\n" + sText + "\n" + sGame + "\nLikes " + sRating,
                       "plotoutline": sAuthor + "\n" + sText + "\n" + sGame + "\nLikes " + sRating,
                       "thumb":       sThumb,
                       "fanart":      sThumb,
                       "credits":     sAuthor},
                      isFolder=False, mediatype="video")

    view.endofdirectory()


def viewBroadcasts(args):
    """Show all broadcasts
    """
    # check inputstream adaptive version
    if StrictVersion(xbmcaddon.Addon(id="inputstream.adaptive").getAddonInfo("version")) < StrictVersion("2.2.19"):
        xbmc.log("[PLUGIN] %s: inputstream.adaptive is too old for broadcasting 2.2.19 is required" % args._addonname, xbmc.LOGERROR)
        view.add_item(args, {"title": args._addon.getLocalizedString(30065)})
        view.endofdirectory()
        return

    # get website
    html = api.getPage(args, "https://steamcommunity.com/apps/allcontenthome/?l=" + args._lang + "&browsefilter=trend&appHubSubSection=13&forceanon=1")
    if not html:
        view.add_item(args, {"title": args._addon.getLocalizedString(30061)})
        view.endofdirectory()
        return

    # parse html
    soup = BeautifulSoup(html, "html.parser")

    # for every list entry
    for div in soup.find_all("div", {"class": "Broadcast_Card"}):
        # get values
        sTitle  = div.find("div", {"class": "apphub_CardContentTitle"}).string.strip()
        sAuthor = div.find("div", {"class": "apphub_CardContentAuthorName"}).a.string.strip()
        sViewer = div.find("div", {"class": "apphub_CardContentViewers"}).string.strip()
        sThumb  = div.find("img", {"class": "apphub_CardContentPreviewImage"})["src"]

        # add to view
        view.add_item(args,
                      {"url":         div.a["href"],
                       "mode":        "videoplay_broadcast",
                       "title":       sAuthor + " - " + sTitle,
                       "tvshowtitle": sAuthor + " - " + sTitle,
                       "plot":        sAuthor + "\n" + sTitle + "\n" + sViewer,
                       "plotoutline": sAuthor + "\n" + sTitle + "\n" + sViewer,
                       "thumb":       sThumb,
                       "fanart":      sThumb,
                       "credits":     sAuthor},
                      isFolder=False, mediatype="video")

    view.endofdirectory()


def viewVideos(args):
    """Show all videos
    """
    # get website
    html = api.getPage(args, "https://steamcommunity.com/apps/allcontenthome/?l=" + args._lang + "&browsefilter=trend&appHubSubSection=3&forceanon=1")
    if not html:
        view.add_item(args, {"title": args._addon.getLocalizedString(30061)})
        view.endofdirectory()
        return

    # parse html
    soup = BeautifulSoup(html, "html.parser")

    # for every list entry
    for div in soup.find_all("div", {"class": "modalContentLink"}):
        # get values
        sTitle  = div.find("div", {"class": "apphub_CardContentTitle"}).string.strip()
        sGame = div.find("div", {"class": "apphub_CardContentType"}).string.strip()
        sThumb  = div.find("img", {"class": "apphub_CardContentPreviewImage"})["src"]
        try:
            sAuthor = div.find("div", {"class": "apphub_CardContentAuthorName"}).a.string.strip()
        except AttributeError:
            sAuthor = div.find("div", {"class": "apphub_CardContentAppName"}).a.string.strip()

        # add to view
        view.add_item(args,
                      {"url":         re.search(r"youtube\.com\/vi\/(.*?)\/0\.jpg", sThumb).group(1),
                       "mode":        "videoplay_youtube",
                       "title":       sAuthor + " - " + sTitle,
                       "tvshowtitle": sAuthor + " - " + sTitle,
                       "plot":        sAuthor + "\n" + sTitle + "\n" + sGame,
                       "plotoutline": sAuthor + "\n" + sTitle + "\n" + sGame,
                       "thumb":       sThumb,
                       "fanart":      sThumb,
                       "credits":     sAuthor},
                      isFolder=False, mediatype="video")

    view.endofdirectory()


class ImageGUI(xbmcgui.WindowDialog):
    def onAction(self, action):
        if action.getId() >= 9:
            self.close()


def startplayback_images(args):
    """Shows an image
    """
    # cache path
    sPath = xbmc.translatePath(args._addon.getAddonInfo("profile"))
    sPath = join(sPath.decode("utf-8"), u"image.jpg")

    # download image
    file = URLopener()
    file.retrieve(args.url, sPath)

    # display image
    item = xbmcgui.ListItem(getattr(args, "title", "Title not provided"), path=sPath)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
    xbmc.executebuiltin("SlideShow(" + xbmc.translatePath(args._addon.getAddonInfo("profile")) + ")")


def startplayback_broadcast(args):
    """Plays a broadcast stream
    """
    # start video
    if u"youtube.com" in args.url:
        item = xbmcgui.ListItem(getattr(args, "title", "Title not provided"), path=args.url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        return True

    # get stream id
    streamid = re.search(r"/watch/(.*?)$", args.url).group(1)

    # get streaming file
    xbmc.log(args.url, xbmc.LOGERROR)
    html = api.getPage(args, "https://steamcommunity.com/broadcast/getbroadcastmpd/?steamid=" + streamid + "&broadcastid=0")
    if not html:
        item = xbmcgui.ListItem(getattr(args, "title", "Title not provided"))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item)
        return

    # parse json
    json_obj = json.loads(html)

    # prepare playback
    item = xbmcgui.ListItem(getattr(args, "title", "Title not provided"), path=json_obj["url"])
    item.setMimeType("application/dash+xml")
    item.setContentLookup(False)

    # inputstream adaptive
    is_helper = inputstreamhelper.Helper("mpd")
    if is_helper.check_inputstream():
        item.setProperty("inputstreamaddon", "inputstream.adaptive")
        item.setProperty("inputstream.adaptive.manifest_type", "mpd")
        # start playback
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


def startplayback_youtube(args):
    """Plays a youtube video
    """
    # start video
    item = xbmcgui.ListItem(getattr(args, "title", "Title not provided"), path="plugin://plugin.video.youtube/play/?video_id=" + args.url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
