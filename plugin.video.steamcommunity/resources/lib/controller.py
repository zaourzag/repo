# -*- coding: utf-8 -*-
# Wakanim - Watch videos from the german anime platform Wakanim.tv on Kodi.
# Copyright (C) 2017 MrKrabat
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

import xbmc
import xbmcgui
import xbmcplugin

from . import api
from . import view


def viewBroadcasts(args):
    """Show all broadcasts
    """
    # get website
    html = api.getPage(args, "https://steamcommunity.com/apps/allcontenthome/?l=german&browsefilter=trend&appHubSubSection=13&forceanon=1&userreviewsoffset=0&broadcastsoffset=0&p=1&numperpage=0&appid=0")
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
                       "mode":        "videoplay",
                       "title":       sAuthor + " - " + sTitle,
                       "tvshowtitle": sAuthor + " - " + sTitle,
                       "plot":        sAuthor + "\n" + sTitle + "\n" + sViewer,
                       "plotoutline": sAuthor + "\n" + sTitle + "\n" + sViewer,
                       "thumb":       sThumb,
                       "fanart":      sThumb,
                       "credits":     sAuthor},
                      isFolder=False, mediatype="video")

    view.endofdirectory()


def startplayback(args):
    """Plays a video
    """
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
