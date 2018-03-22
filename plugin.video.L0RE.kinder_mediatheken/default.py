#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os,json

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
json_addons='{"elements":[{"name":"Disney","id":"plugin.video.L0RE.disneychannel"},{"name":"Nickolodion","id":"plugin.video.nick_de"},{"id":"plugin.video.L0RE.kividoo","name":"Kividoo"}'
json_addons=json_addons+',{"id":"plugin.video.kikamediathek","name":"Kika Mediathek"},{"id":"plugin.video.funkmediathek","name":"Funk Mediathek"},{"id":"plugin.video.sesamstrasse_de","name":"Sesamstrasse"}'
json_addons=json_addons+',{"id":"plugin.video.zdftivi","name":"ZDF Tivi"},{"id":"plugin.video.kika_de","name":"KIKA+"},{"id":"plugin.video.wdrmaus","name":"WDR Maus"}'
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
if  addon.getSetting("plugin.video.netzkino_de")=="true":       
        addDir("Netzkino","plugin://plugin.video.netzkino_de/category/35/",'special://home/addons/plugin.video.netzkino_de/icon.png')        
if  addon.getSetting("plugin.video.maxdome")=="true":       
        addDir("Maxdome","plugin://plugin.video.maxdome/?action=list&page=kids",'special://home/addons/plugin.video.maxdome/icon.png')                
if  addon.getSetting("plugin.video.skygo.de")=="true":       
        addDir("Skygo","plugin://plugin.video.skygo.de/?action=listPage&id=10",'special://home/addons/plugin.video.skygo.de/icon.png')                              
xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      