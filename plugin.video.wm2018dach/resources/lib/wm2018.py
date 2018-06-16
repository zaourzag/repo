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

import sys
import inputstreamhelper

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

from . import view
from . import model


def main():
    """Main function for the addon
    """
    args = model.parse()

    # inputstream adaptive settings
    if hasattr(args, "mode") and args.mode == "hls":
        is_helper = inputstreamhelper.Helper("hls")
        if is_helper.check_inputstream():
            xbmcaddon.Addon(id="inputstream.adaptive").openSettings()
        return True

    # list menue
    xbmcplugin.setContent(int(sys.argv[1]), "tvshows")
    check_mode(args)


def check_mode(args):
    """Run mode-specific functions
    """
    if hasattr(args, "mode"):
        mode = args.mode
    else:
        mode = None

    if not mode:
        showMainMenue(args)
    elif mode == "videoplay":
        startplayback(args)
    else:
        # unkown mode
        xbmc.log("[PLUGIN] %s: Failed in check_mode '%s'" % (args._addonname, str(mode)), xbmc.LOGERROR)
        xbmcgui.Dialog().notification(args._addonname, args._addon.getLocalizedString(30061), xbmcgui.NOTIFICATION_ERROR)
        showMainMenue(args)


def showMainMenue(args):
    """Show main menu
    """
    # football matches
    matches = {"0": "https://wm2018.akamaized.net/hls/live/625036/wm2018/master.m3u8?b=0-", # ARD
               "1": "https://zdf1314-lh.akamaihd.net/i/de14_v1@392878/master.m3u8?", # ZDF
               "2": "http://orf1ad.orf.cdn.ors.at/out/u/orf1ad/qxb/manifest.m3u8", # ORF
               "3": "http://ors-uhd.cdn.ors.at/out/u/orfuhd-abr-hdr10_1.m3u8"} # ORF UHD

    # press conference
    conference = {"0": "https://wdrardevent1-lh.akamaihd.net/i/ardevent1_weltweit@566648/master.m3u8?b=0-", # ARD
                  "1": "https://zdf0506-lh.akamaihd.net/i/de06_v1@392858/master.m3u8?", # ZDF
                  "2": False, # ORF
                  "3": False} # ORF UHD


    if matches[args._addon.getSetting("stream")]:
        view.add_item(args,
                      {"title": args._addon.getLocalizedString(30040),
                       "url":   matches[args._addon.getSetting("stream")],
                       "mode":  "videoplay"},
                      isFolder=False)
    if conference[args._addon.getSetting("stream")]:
        view.add_item(args,
                      {"title": args._addon.getLocalizedString(30041),
                       "url":   conference[args._addon.getSetting("stream")],
                       "mode":  "videoplay"},
                      isFolder=False)

    view.endofdirectory()


def startplayback(args):
    """Plays a stream
    """
    # prepare playback
    item = xbmcgui.ListItem(getattr(args, "title", "Title not provided"), path=args.url)
    item.setMimeType("application/vnd.apple.mpegurl")
    item.setContentLookup(False)

    # inputstream adaptive
    is_helper = inputstreamhelper.Helper("hls")
    if args._addon.getSetting("inputstream_adaptive_active") == "true" and is_helper.check_inputstream():
        item.setProperty("inputstreamaddon", "inputstream.adaptive")
        item.setProperty("inputstream.adaptive.manifest_type", "hls")

    # start playback
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
