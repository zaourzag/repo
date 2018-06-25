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

import inputstreamhelper

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

from . import view
from . import model


def main(argv):
    """Main function for the addon
    """
    args = model.parse(argv)

    # inputstream adaptive settings
    if hasattr(args, "mode") and args.mode == "hls":
        is_helper = inputstreamhelper.Helper("hls")
        if is_helper.check_inputstream():
            xbmcaddon.Addon(id="inputstream.adaptive").openSettings()
        return True

    # list menue
    xbmcplugin.setContent(int(args._argv[1]), "tvshows")
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
    # stream files
    streams = {"0": {"Fußballspiel live":    "https://wm2018.akamaized.net/hls/live/625036/wm2018/master.m3u8?b=0-", # ARD
                     "Pressekonferenz live": "https://wdrardevent1-lh.akamaihd.net/i/ardevent1_weltweit@566648/master.m3u8?b=0-"},

               "1": {"Fußballspiel live":    "https://zdf1314-lh.akamaihd.net/i/de14_v1@392878/master.m3u8?", # ZDF
                     "Draufsicht 1 live":    "http://zdf0304-lh.akamaihd.net/i/de03_v1@392855/master.m3u8",
                     "Draufsicht 2 live":    "http://zdf0506-lh.akamaihd.net/i/de05_v1@392857/master.m3u8",
                     "Trainersicht live":    "http://zdf0304-lh.akamaihd.net/i/de04_v1@392856/master.m3u8",
                     "Pressekonferenz live": "https://zdf0506-lh.akamaihd.net/i/de06_v1@392858/master.m3u8?"},

               "2": {"720p adaptive live": "http://orf1ad.orf.cdn.ors.at/out/u/orf1ad/qxb/manifest.m3u8", # ORF
                     "4K HDR live":        "http://ors-uhd.cdn.ors.at/out/u/orfuhd-abr-hdr10_1.m3u8",
                     "2K HDR live":        "http://ors-uhd.cdn.ors.at/out/u/orfuhd-abr-hdr10_2.m3u8",
                     "1080p HDR live":     "http://ors-uhd.cdn.ors.at/out/u/orfuhd-abr-hdr10_3.m3u8",
                     "720p HDR live":      "http://ors-uhd.cdn.ors.at/out/u/orfuhd-abr-hdr10_4.m3u8"},

               "3": {"Fußballspiel live": "https://srgssruni2ch-lh.akamaihd.net/i/enc2uni_ch@191041/master.m3u8?dw=0"}, # SRF
               "4": {"Fußballspiel live": "https://srgssruni10ch-lh.akamaihd.net/i/enc10uni_ch@191367/master.m3u8?dw=0"}, # RTS
               "5": {"Fußballspiel live": "https://srgssrgop20a-lh.akamaihd.net/i/enc20a_gop@141646/master.m3u8?dw=0"}, # RSI

               "6": {"Fußballspiel live": "https://onelivestream-lh.akamaihd.net/i/one_livestream@568814/master.m3u8"}, # ONE ARD
               "7": {"Fußballspiel live": "https://zdf1112-lh.akamaihd.net/i/de12_v1@392882/master.m3u8?dw=0"} # ZDFInfo
              }


    # create directory
    for key, value in list(streams[args._addon.getSetting("stream")].items()):
        view.add_item(args,
                      {"title": key,
                       "url":   value,
                       "mode":  "videoplay"},
                      isFolder=False)

    view.endofdirectory(args)


def startplayback(args):
    """Plays a stream
    """
    # prepare playback
    item = xbmcgui.ListItem(getattr(args, "title", "Title not provided"), path=args.url)
    item.setMimeType("application/vnd.apple.mpegurl")
    item.setContentLookup(False)

    # inputstream adaptive
    is_helper = inputstreamhelper.Helper("hls")
    if not args._addon.getSetting("stream") == "2" and not args._addon.getSetting("stream") == "6" and args._addon.getSetting("inputstream_adaptive_active") == "true" and is_helper.check_inputstream():
        item.setProperty("inputstreamaddon", "inputstream.adaptive")
        item.setProperty("inputstream.adaptive.manifest_type", "hls")

    # start playback
    xbmcplugin.setResolvedUrl(int(args._argv[1]), True, item)
