#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os,json

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
json_addons='{"elements":[{"name":"Disney","id":"plugin.video.L0RE.disneychannel"},{"name":"Nickolodion","id":"plugin.video.nick_de"},{"id":"plugin.video.L0RE.kividoo","name":"Kividoo"}'
json_addons=json_addons+',{"id":"plugin.video.kikamediathek","name":"Kika Mediathek"},{"id":"plugin.video.funkmediathek","name":"Funk Mediathek"},{"id":"plugin.video.sesamstrasse_de","name":"Sesamstrasse"}'
json_addons=json_addons+']}'
print(json_addons)
struktur = json.loads(json_addons)  
print(struktur)

def addDir(name, url,iconimage):  
  u =url  
  liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name})  
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok


for element in struktur["elements"] :
   print("Element")
   print(element)
   enabled=addon.getSetting(element["id"])=="true"
   print(enabled)
   icon_addon=xbmc.translatePath('special://home/addons/'+element["id"]+'/icon.png')
   if enabled:
        addDir(element["name"],"plugin://"+element["id"],icon_addon)
xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      