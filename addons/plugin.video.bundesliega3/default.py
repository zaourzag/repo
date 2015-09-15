#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import urlparse
import urllib, urllib2, socket, cookielib, re, os, shutil,json
import time
import locale
from datetime import datetime


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString

Monate = {
           "Januar":1,
           "Februar":2,
           "März":3,
           "April":4,
           "Mai":5,
           "Juni":6,
           "Juli":7,
           "August":8,
           "September":9,
           "Oktober":10,
           "November":11,
           "Dezember":12
}


def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 


def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
def addLink(name, url, mode,meldung=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&meldung="+ str(meldung)
	liz = xbmcgui.ListItem(name)
	liz.setProperty('IsPlayable', 'true')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok
  
  
def geturl(url):
   cj = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
   opener.addheaders = [('User-Agent', userAgent)]
   req = opener.open(url)
   inhalt = req.read()   
   return inhalt
   
  
def get_spiele():
  URL="http://www.liga3-online.de/live-spiele/"
  content=geturl(URL)
  kurz_inhalt = content[content.find('wp-table-reloaded wp-table-reloaded-id-8')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</tbody>')]
  spl=kurz_inhalt.split('<tr class="row')
  for i in range(2,len(spl)-1,1):
    element=spl[i]
    debug ("Element :" + element)
    ar_datum=re.compile('<td class="column-2[^>]*>([^<]+)</td>', re.DOTALL).findall(element)    
    ar_zeit=re.compile('<td class="column-3[^>]*>([^<]+)</td>', re.DOTALL).findall(element)    
    ar_spiel=re.compile('<td class="column-4[^>]*>([^<]+)</td>', re.DOTALL).findall(element)
    ar_sender=re.compile('<td class="column-5[^>]*>([^<]+)</td>', re.DOTALL).findall(element)
    if ar_datum:
     datum=ar_datum[0]
     datum_old=datum
    else:
     datum=datum_old
    if ar_zeit :
      zeit=ar_zeit[0]
      zeit_old=zeit
    else:
      zeit=zeit_old
    spiel=ar_spiel[0]
    sender=ar_sender[0]
    lt = time.localtime()
    jahr=time.strftime("%Y", lt)
    debug("datum"+datum)
    datum_reg=re.compile('.+, ([0-9]+)\. (.+)', re.DOTALL).findall(datum)
    month=datum_reg[0][1]
    day=datum_reg[0][0]
    monat=Monate[month]
    zeitstring=day+"."+str(monat) +"."+jahr + " " + zeit
    zeitobjekt=time.strptime(zeitstring , "%d.%m.%Y %H:%M Uhr")
    neuzeit=time.strftime("%d. %B %H:%M",zeitobjekt)
    debug("BL3 :" + datum +" # "+ zeit + " # "+ spiel + " # " + sender)    
    now=time.time()

    if time.mktime(zeitobjekt) > time.mktime(lt) :
       meldung="Läuft noch nicht"
       debug ("XXXXXXXXXX Meldung")
    else:
       meldung=""
    addLink(name=neuzeit +" : "+ spiel, url=sender , mode="Watch",meldung=meldung)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def watchlive(url,meldung=""):
   urlnew=""
   if not meldung == "" :
        dialog = xbmcgui.Dialog()
        nr=dialog.yesno("Läuft nicht", "Dieses Spielt läuft noch nicht trotzdem versuchen?")
        if not nr:
          listitem = xbmcgui.ListItem(path=url) 
          xbmcplugin.setResolvedUrl(addon_handle,False, listitem) 
          get_spiele()
        else:
          if "MDR" in url:
            urlnew="http://mdr_sa_hls-lh.akamaihd.net/i/livetvmdrsachsenanhalt_de@106901/master.m3u8"       
          if url=="mdr.de":
            urlnew="http://mdr_event1_hls-lh.akamaihd.net/i/livetvmdrevent1_de@106904/index_1728_av-p.m3u8?sd=10&rebase=on"    
          if url=="WDR":
            urlnew="http://wdr_fs_geo-lh.akamaihd.net/i/wdrfs_geogeblockt@112044/master.m3u8"             
          if url=="NDR":
            urlnew="http://ndr_fs-lh.akamaihd.net/i/ndrfs_nds@119224/master.m3u8"            
          if urlnew :         
             listitem = xbmcgui.ListItem(path=urlnew) 
             xbmcplugin.setResolvedUrl(addon_handle,True, listitem)
          else :
             nr=dialog.ok("Sender nicht bekannt", "Zu Diesem sender fehlt der stream")
             listitem = xbmcgui.ListItem(path=url) 
             xbmcplugin.setResolvedUrl(addon_handle,False, listitem) 
  
  
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
meldung = urllib.unquote_plus(params.get('meldung', ''))
  
  
if mode is '':
    get_spiele()
if mode == 'Watch':
    watchlive(url=url,meldung=meldung)
  
  

