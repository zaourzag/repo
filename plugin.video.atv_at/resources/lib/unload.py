# -*- coding: utf-8 -*-
# 22.09.2018 - ©realvito

import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
PY2 = sys.version_info[0] == 2
if PY2:
	try:
		import StorageServer
	except ImportError:
		from . import storageserverdummy as StorageServer

addon = xbmcaddon.Addon('plugin.video.atv_at')


class Unload:
	def __init__(self, *args, **kwargs):
		if sys.argv[1] == "loeschen":
			cache = StorageServer.StorageServer(addon.getAddonInfo('id'))
			cache.delete("%")
			xbmc.sleep(2000)
			xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30501))


def translation(id):
	LANGUAGE = addon.getLocalizedString(id)
	if PY2 and isinstance(LANGUAGE, unicode):
		LANGUAGE = LANGUAGE.encode('utf-8')
	return LANGUAGE


def Main():
	if PY2:
		Unload()
	else:
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30502))


if __name__ == "__main__":
	Main()
