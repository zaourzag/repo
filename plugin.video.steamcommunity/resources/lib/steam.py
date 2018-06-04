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
import random
import inputstreamhelper

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

from . import api
from . import view
from . import model
from . import controller


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
    api.start(args)
    xbmcplugin.setContent(int(sys.argv[1]), "tvshows")
    check_mode(args)
    api.close(args)


def check_mode(args):
    """Run mode-specific functions
    """
    if hasattr(args, "mode"):
        mode = args.mode
    else:
        mode = None

    if not mode:
        showMainMenue(args)

    elif mode == "queue":
        pass #controller.showQueue(args)
    elif mode == "search":
        pass #controller.searchAnime(args)
    elif mode == "history":
        pass #controller.showHistory(args)
    elif mode == "random":
        pass #controller.showRandom(args)

    elif mode == "broadcasts":
        controller.viewBroadcasts(args)
    elif mode == "episodes":
        pass #controller.viewEpisodes(args)
    elif mode == "videoplay":
        controller.startplayback(args)
    else:
        # unkown mode
        xbmc.log("[PLUGIN] %s: Failed in check_mode '%s'" % (args._addonname, str(mode)), xbmc.LOGERROR)
        xbmcgui.Dialog().notification(args._addonname, args._addon.getLocalizedString(30061), xbmcgui.NOTIFICATION_ERROR)
        showMainMenue(args)


def showMainMenue(args):
    """Show main menu
    """
    view.add_item(args,
                  {"title": args._addon.getLocalizedString(30040),
                   "mode":  "search_hub"})
    view.add_item(args,
                  {"title": args._addon.getLocalizedString(30041),
                   "mode":  "search_user"})

    #view.add_item(args,
                  #{"title": args._addon.getLocalizedString(30050),
                   #"mode":  "all"})
    view.add_item(args,
                  {"title": args._addon.getLocalizedString(30051),
                   "mode":  "screenshots"})
    view.add_item(args,
                  {"title": args._addon.getLocalizedString(30052),
                   "mode":  "artwork"})
    view.add_item(args,
                  {"title": args._addon.getLocalizedString(30053),
                   "mode":  "broadcasts"})
    view.add_item(args,
                  {"title": args._addon.getLocalizedString(30054),
                   "mode":  "videos"})
    #view.add_item(args,
                  #{"title": args._addon.getLocalizedString(30055),
                   #"mode":  "workshop"})
    #view.add_item(args,
                  #{"title": args._addon.getLocalizedString(30056),
                   #"mode":  "news"})
    #view.add_item(args,
                  #{"title": args._addon.getLocalizedString(30057),
                   #"mode":  "guides"})
    #view.add_item(args,
                  #{"title": args._addon.getLocalizedString(30058),
                   #"mode":  "reviews"})
    view.endofdirectory()
