#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcplugin
import xbmcaddon
import xbmcgui
import datetime
import sys
import re
import os
import json
import resources.lib.subtitle as subtitle
#from resources.lib.listcache import listcache
from resources.lib.rssparser import parser as rssParser
from resources.lib.listing import getAZ# as getAZ
from resources.lib.listing import getAllAZ# as getAllAZ
from resources.lib.listing import getVideosXml# as getVideosXml
#import resources.lib.scraper

#import f4mproxy
#import ardlib
#from ardlib import parser as rssParser
#from ardlib import getAZ as getAZ
#from ardlib import getAllAZ as getAllAZ
#from ardlib import getVideosXml as getVideosXml
import string
import random
import time
#import f4mproxy

#resources.lib.scraper()

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.ardmediathek_de'
addon = xbmcaddon.Addon(id=addonID)
subFile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')+'/sub.srt').decode('utf-8')
if addon.getSetting("firstrun") != 'false':
  addon.setSetting("firstrun", 'false')
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
baseUrl = "http://www.ardmediathek.de"
showSubtitles = addon.getSetting("showSubtitles") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
#showDateInTitle=addon.getSetting("showDateInTitle") == "true"
showDateInTitle = False
viewMode = str(addon.getSetting("viewIDVideos"))
viewModeShows = str(addon.getSetting("viewIDShows"))
defaultThumb = baseUrl+"/ard/static/pics/default/16_9/default_webM_16_9.jpg"
defaultBackground = "http://www.ard.de/pool/img/ard/background/base_xl.jpg"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
#icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
#channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/favs.new")
#mdrHd = addon.getSetting("mdrHd") == "true"
mdrHd = int(addon.getSetting("videoQuality")) == 3
videoQuality = int(addon.getSetting("videoQuality"))
listLive = addon.getSetting("listLive") == "true"
helix=True
helix=False

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def index():
  #addDir(translation(30011), "", 'listShowsFavs', "")
  #addDir(translation(30001), baseUrl+"/tv/Neueste-Videos/mehr?documentId=21282466"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30001), baseUrl+"/tv/Neueste-Videos/mehr?documentId=23644268"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)#listet auch zukünftige sendungen
  addDir(translation(30002), baseUrl+"/tv/Meistabgerufene-Videos/mehr?documentId=21282514"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30005), "", 'listShowsAZMain', "")
  addDir(translation(30020), "", 'listChannels', "")
  addDir(translation(30006), "mehr", 'listCats', "")
  addDir(translation(30007), baseUrl+"/tv/Dossiers/mehr?documentId=21301810&rss=true", 'listDirRss', "")
  addDir(translation(30014), "", 'listEinsLike', "")
  addDir(translation(30039), "", 'listFootball', "")
  addDir(translation(30008), "", 'search', "")
  if listLive:
    addDir(translation(30013), "", 'listLiveChannels', "")
  xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(url,page=1):
  content = getUrl(url)
  spl = content.split('<div class="teaser" data-ctrl')
  for i in range(1, len(spl), 1):
    entry = spl[i]
    match = re.compile('documentId=(.+?)&', re.DOTALL).findall(entry)
    videoID = match[0]
    matchTitle = re.compile('class="headline">(.+?)<', re.DOTALL).findall(entry)
    match = re.compile('class="dachzeile">(.+?)<', re.DOTALL).findall(entry)
    if match and match[0].endswith("Uhr"):
      date = match[0]
      date = date.split(" ")[0]
      date = date[:date.rfind(".")]
      if showDateInTitle:
        title = date+" - "+matchTitle[0]
    elif match:
      title = match[0]+" - "+matchTitle[0]
    else:
      title = matchTitle[0]
    match = re.compile('class="subtitle">(.+?) \\| (.+?) min(.+?)</p>', re.DOTALL).findall(entry)
    match2 = re.compile('class="subtitle">(.+?) min.*?</p>', re.DOTALL).findall(entry)
    duration = ""
    desc = ""
    if match:
      date = match[0][0]
      date = date[:date.rfind(".")]
      duration = match[0][1]
      channel = match[0][2].replace("<br/>","")
      if "00:" in duration:
        duration = 1
      if showDateInTitle:
        title = date+" - "+title
      desc = channel+" ("+date+")\n"+title
    elif match2:
      duration = match2[0]
      if "00:" in duration:
        duration = 1
    title = cleanTitle(title)
    match = re.compile('/image/(.+?)/16x9/', re.DOTALL).findall(entry)
    thumb = ""
    if match:
      thumb = baseUrl+"/image/"+match[0]+"/16x9/448"
    addLink(title, videoID, 'playVideo', thumb, duration, desc)
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')
    
def listVideosXml(videoId):
  for name,id,thumb,length in getVideosXml(videoId):
    addLink(name, id, 'playVideo', thumb, runtimeToInt(length), '')
  xbmcplugin.endOfDirectory(pluginhandle)
  
def listDirRss(url):
  content = getUrl(url)
  for title,pubDate,thumb,plot,link,documentId,category,runtime in rssParser(content):
    if not checkLive(pubDate):
      addDir(title, documentId, 'listVideosXml', thumb)#TODO plot
  xbmcplugin.endOfDirectory(pluginhandle)

def listVideosRss(url,showName,hideShowName,nextPage,einsLike):
  debug("listVideosRss url :"+ url)
  content = getUrl(url)
  c = rssParser(content)
  for title,pubDate,thumb,plot,link,documentId,category,runtime in c:
    if hideShowName:
      title = title.replace(showName+' - ','')
    if not checkLive(pubDate) and not '/Audio-Podcast?' in link and not '/Video-Podcast?' in link:
      thumb = thumb.replace('/384','/448')
      addLink(cleanTitle(title[0].upper()+title[1:]),link,'playVideoUrl',thumb,runtime,desc=plot,genre=category)
      
  if len(c) > 45 and nextPage:#ARD Webseite ist buggy, darum nicht 50 oder 54
    if einsLike:#einslike next page "hack"
      nextPageUrlBit = '&mcontent=page.'
    else:
      nextPageUrlBit = '&mcontents=page.'
    if not nextPageUrlBit in url:
      url += nextPageUrlBit+'2'
    else:
      url = url.replace(nextPageUrlBit+url.split(nextPageUrlBit)[-1],nextPageUrlBit+str(int(url.split(nextPageUrlBit)[-1])+1))
    if hideShowName:
      addShowDir(translation(30009).encode("utf-8"), url, 'listVideosRss', "", showName)
    elif einsLike: 
      addDir(translation(30009).encode("utf-8"), url, 'listVideosRss', "", nextPage=True, einsLike=True)
    else:
      addDir(translation(30009).encode("utf-8"), url, 'listVideosRss', "", nextPage=True, einsLike=False)
    
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def runtimeToInt(runtime):
  t = runtime.replace('Min','').replace('min','').replace('.','').replace(' ','')
  HHMM = t.split(':')
  return int(HHMM[0])*60 + int(HHMM[1])

def checkLive(date):
  date = date.replace(' '+date.split(' ')[-1],'')#python 2.7 doesnt support %z
  #dateEpoch = time.mktime(time.strptime(date,"%a, %d %b %Y %H:%M:%S %z"))
  dateEpoch = time.mktime(time.strptime(date,"%a, %d %b %Y %H:%M:%S"))+3600
  #return time.time() < dateEpoch
  return False

def videovontag(content):
        entry=content
        bild=""
        for i2 in range(1, len(entry), 1):
                entrylink = '<a href="/'+ entry[i2]                 
                if "mediaLink"  in entrylink:
                  bild=""
                  match = re.compile('urlScheme&#039;:&#039;(.+?)#', re.DOTALL).findall(entrylink)
                  bild=baseUrl+ match[0] +"640"
                if "textLink"   in entrylink:
                     videoID=""
                     match = re.compile('documentId=(.+?)"', re.DOTALL).findall(entrylink)
                     if match:
                       videoID = match[0]  
                       debug ("videoID: "+ videoID)
                     match = re.compile('<h4 class="headline">(.+?)</h4>', re.DOTALL).findall(entrylink)    
                     if match:
                       titlev=match[0]
                       debug ("titlev: "+ titlev)
                       debug ("bild: "+ bild)
                     match = re.compile('<p class="subtitle">([0-9]+)', re.DOTALL).findall(entrylink)    
                     if match:
                       debug("DAUER:" + match[0])
                       duration=int(match[0])*60                       
                     else:
                        duration=0
                     if videoID:
                        debug("Addlink")
                        addLink(cleanTitle(titlev), videoID, 'playVideo', bild,duration=duration) 
def toeteenden(LISTE,content,zeiten):
   for  zeiten2 in LISTE:
            teile2='<div class="entry" data-ctrl-'+zeiten+"collapse-entry="
            content = content[:content.find(teile2)]
   content = content[:content.find('<div class="section onlyWithJs sectionA">')]           
   content = content[:content.find('<div class="box" data-ctrl-timeRangecollapse')]  
   return content
    
def listChannelVideos(url):
  LISTE=["MORGEN","NACHMITTAG","VORABEND","ABEND"]
  content = getUrl(url)  
  
  for  zeiten in LISTE:
    debug("** "+zeiten +" **")
    teile='<div class="entry" data-ctrl-'+zeiten+"collapse-entry="    
    spl = content.split(teile)
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if '<div class="entry" data-ctrl-' in entry:
          entry=toeteenden(LISTE,entry,zeiten)                                 
          match = re.compile('class="titel">(.+?)<', re.DOTALL).findall(entry)           
          title = match[0]
          match = re.compile('class="date">(.+?)<', re.DOTALL).findall(entry)
          datum = match[0]
          titleshow = datum +" - "+ title
          spl2 = entry.split('<a href="/')
          if len(spl2) >3:            
             addDir(cleanTitle(titleshow), url, 'listfilesofshow', icon,title=title)
          else:
            videovontag(spl2)           
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')
         
  
def listfilesofshow(url,title):
  LISTE=["MORGEN","NACHMITTAG","VORABEND","ABEND"]
  content = getUrl(url)    
  for  zeiten in LISTE:
    debug("** "+zeiten +" **")
    teile='<div class="entry" data-ctrl-'+zeiten+"collapse-entry="    
    spl = content.split(teile)
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if '<div class="entry" data-ctrl-' in entry:
          entry=toeteenden(LISTE,entry,zeiten)                                  
          #debug("--------------")
          #debug(entry)
          #debug("--------------")
          match = re.compile('class="titel">(.+?)<', re.DOTALL).findall(entry)           
          titleshow = match[0]
          
          debug("### ####"+ title)
          debug("### ####"+ titleshow)
          if titleshow==title:           
            spl2 = entry.split('<a href="/')
            videovontag(spl2)                         
  debug("#####:")
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listLiveChannels():
  addLink("Das Erste", "", "playLiveARD", "http://m-service.daserste.de/appservice/1.4.1/image/broadcast/fallback/jpg/512")
  content = getUrl(baseUrl+"/tv/live?kanal=Alle")
  spl = content.split('<div class="teaser" data-ctrl')
  for i in range(1, len(spl), 1):
    entry = spl[i]
    match = re.compile('kanal=(.+?)"', re.DOTALL).findall(entry)
    channelID = match[0]
    match = re.compile('class="headline">(.+?)<', re.DOTALL).findall(entry)
    title = match[0]
    match = re.compile('/image/(.+?)/16x9/', re.DOTALL).findall(entry)
    thumb = baseUrl+"/image/"+match[0]+"/16x9/448"
    if title!="Das Erste":
      addLink(cleanTitle(title), channelID, 'playLive', thumb)
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def listShowsAZMain():
  addDir("0-9", "0-9", 'listShowsAZ', "")
  letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
  for letter in letters:
    addDir(letter.upper(), letter.upper(), 'listShowsAZ', "")
  xbmcplugin.endOfDirectory(pluginhandle)


def listShowsAZ(letter):
  items = getAllAZ(letter)
  xbmcplugin.addDirectoryItems(int(sys.argv[1]), items)
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')
  """
  for title,url,thumb in getAZ(letter):
    addShowDir(cleanTitle(title), baseUrl+url+'&m23644322=quelle.tv&rss=true', 'listVideosRss', thumb, cleanTitle(title))
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')
  """
def listShowsFavs():
  xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
  if os.path.exists(channelFavsFile):
    fh = open(channelFavsFile, 'r')
    all_lines = fh.readlines()
    for line in all_lines:
      title = line[line.find("###TITLE###=")+12:]
      title = title[:title.find("#")]
      url = line[line.find("###URL###=")+10:]
      url = url[:url.find("#")]
      thumb = line[line.find("###THUMB###=")+12:]
      thumb = thumb[:thumb.find("#")]
      addShowFavDir(title, urllib.unquote_plus(url), "listVideos", thumb)
    fh.close()
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def listEinsLike():
  addDir(translation(30001), baseUrl+"/einslike/Neueste-Videos/mehr?documentId=21282466"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30002), baseUrl+"/einslike/Meistabgerufene-Videos/mehr?documentId=21282464"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30015), baseUrl+"/einslike/Musik/mehr?documentId=21301894"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30016), baseUrl+"/einslike/Leben/mehr?documentId=21301896"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30017), baseUrl+"/einslike/Netz-Tech/mehr?documentId=21301898"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30018), baseUrl+"/einslike/Info/mehr?documentId=21301900"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30019), baseUrl+"/einslike/Spa%C3%9F-Fiktion/mehr?documentId=21301902"+'&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listChannels():
  addDir("Das Erste", "208", 'listChannel', icon)
  addDir("BR", "2224", 'listChannel', icon)
  addDir("HR", "5884", 'listChannel', icon)
  addDir("MDR", "5882", 'listChannel', icon)
  addDir("NDR", "5906", 'listChannel', icon)
  addDir("RB", "5898", 'listChannel', icon)
  addDir("RBB", "5874", 'listChannel', icon)
  addDir("SR", "5870", 'listChannel', icon)
  addDir("SWR", "5310", 'listChannel', icon)
  addDir("WDR", "5902", 'listChannel', icon)
  addDir("Tagesschau24", "5878", 'listChannel', icon)
  addDir("EinsPlus", "4178842", 'listChannel', icon)
  addDir("EinsFestival", "673348", 'listChannel', icon)
  #addDir("DW-TV", "5876", 'listChannel', icon)
  xbmcplugin.endOfDirectory(pluginhandle)


def listChannel(channel):
  addDir(translation(30040), baseUrl+"/tv/sendungVerpasst?kanal="+channel+"&tag=0", 'listChannelVideos', "")
  addDir(translation(30041), baseUrl+"/tv/sendungVerpasst?kanal="+channel+"&tag=1", 'listChannelVideos', "")
  addDir((datetime.date.today()-datetime.timedelta(days=2)).strftime("%b %d, %Y"), baseUrl+"/tv/sendungVerpasst?kanal="+channel+"&tag=2", 'listChannelVideos', "")
  addDir((datetime.date.today()-datetime.timedelta(days=3)).strftime("%b %d, %Y"), baseUrl+"/tv/sendungVerpasst?kanal="+channel+"&tag=3", 'listChannelVideos', "")
  addDir((datetime.date.today()-datetime.timedelta(days=4)).strftime("%b %d, %Y"), baseUrl+"/tv/sendungVerpasst?kanal="+channel+"&tag=4", 'listChannelVideos', "")
  addDir((datetime.date.today()-datetime.timedelta(days=5)).strftime("%b %d, %Y"), baseUrl+"/tv/sendungVerpasst?kanal="+channel+"&tag=5", 'listChannelVideos', "")
  addDir((datetime.date.today()-datetime.timedelta(days=6)).strftime("%b %d, %Y"), baseUrl+"/tv/sendungVerpasst?kanal="+channel+"&tag=6", 'listChannelVideos', "")
  xbmcplugin.endOfDirectory(pluginhandle)


def listCats(type):
  addDir(translation(30036), baseUrl+"/tv/Comedy-Satire/mehr?documentId=26405766"           + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30004), baseUrl+"/tv/Ausgewählte-Filme/mehr?documentId=33649088"         + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30018), baseUrl+"/tv/Info/mehr?documentId=21301900"                    + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30031), baseUrl+"/tv/Kinder-Familie/mehr?documentId=21282542"          + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30032), baseUrl+"/tv/Kultur/mehr?documentId=21282546"                  + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30016), baseUrl+"/tv/Leben/mehr?documentId=21301896"                   + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30015), baseUrl+"/tv/Musik/mehr?documentId=21301894"                   + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30017), baseUrl+"/tv/Netz-Tech/mehr?documentId=21301898"               + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  #addDir(translation(30003), baseUrl+"/tv/Reportage-Doku/mehr?documentId=21301806"          + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30003), baseUrl+"/tv/Reportage-Dokumentation/mehr?documentId=22651276" + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30033), baseUrl+"/tv/Satire-Unterhaltung/mehr?documentId=21282544"     + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30035), baseUrl+"/tv/Serien-Soaps/mehr?documentId=21282548"            + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30019), baseUrl+"/tv/Spa%C3%9F-Fiktion/mehr?documentId=21301902"       + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30038), baseUrl+"/tv/Sport-in-der-Mediathek/mehr?documentId=26439062"  + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30037), baseUrl+"/tv/Videos-für-Kinder/mehr?documentId=22651194"       + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30034), baseUrl+"/tv/Wissen/mehr?documentId=21282530"                  + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def listFootball():
  addDir(translation(30080), baseUrl+"/tv/Alle-Videos-zu-Eintracht-Frankfurt/mehr?documentId=22775344"           + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30081), baseUrl+"/tv/Alle-Videos-zu-Schalke-04/mehr?documentId=22775352"                    + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30082), baseUrl+"/tv/Alle-Videos-zum-VfB-Stuttgart/mehr?documentId=22775376"                + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30083), baseUrl+"/tv/Alle-Videos-zu-1899-Hoffenheim/mehr?documentId=22775328"               + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30084), baseUrl+"/tv/Alle-Videos-zum-SC-Paderborn/mehr?documentId=22775372"                 + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30085), baseUrl+"/tv/Alle-Videos-zum-SC-Freiburg/mehr?documentId=22552050"                  + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30086), baseUrl+"/tv/Alle-Videos-zu-Hannover-96/mehr?documentId=22775360"                   + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30087), baseUrl+"/tv/Alle-Videos-zu-Werder-Bremen/mehr?documentId=22775384"                 + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30088), baseUrl+"/tv/Alle-Videos-zu-Bayer-Leverkusen/mehr?documentId=22775332"              + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30089), baseUrl+"/tv/Alle-Videos-zum-VfL-Wolfsburg/mehr?documentId=22775380"                + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30090), baseUrl+"/tv/Alle-Videos-zum-Hamburger-SV/mehr?documentId=22775356"                 + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30091), baseUrl+"/tv/Alle-Videos-zum-FSV-Mainz-05/mehr?documentId=22775368"                 + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30092), baseUrl+"/tv/Alle-Videos-zu-Bayern-M%C3%BCnchen/mehr?documentId=22775336"           + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30093), baseUrl+"/tv/Alle-Videos-zum-1-FC-K%C3%B6ln/mehr?documentId=22775294"               + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30094), baseUrl+"/tv/Alle-Videos-zu-Borussia-M%C3%B6nchengladbach/mehr?documentId=22775340" + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30095), baseUrl+"/tv/Alle-Videos-zu-Hertha-BSC/mehr?documentId=22775364"                    + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30096), baseUrl+"/tv/Alle-Videos-zum-FC-Augsburg/mehr?documentId=22775348"                  + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  addDir(translation(30097), baseUrl+"/tv/Alle-Videos-zu-Borussia-Dortmund/mehr?documentId=22552316"             + '&m23644322=quelle.tv&rss=true', 'listVideosRss', "", nextPage=True, einsLike=True)
  xbmcplugin.addSortMethod(pluginhandle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
  xbmcplugin.endOfDirectory(pluginhandle)
  if forceViewMode:
    xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def playVideo(videoID):
  playVideoUrl(baseUrl+"/tv/?documentId="+videoID,videoID)

def playVideoUrl(url,videoID=False):
  if not videoID:
    videoID = url.split('documentId=')[1]
    if '&' in videoID:
      videoID = videoID.split('&')[0]
  debug("playVideoUrl url :"+url)
  content = getUrl(url)
  match = re.compile('<div class="box fsk.*?class="teasertext">(.+?)</p>', re.DOTALL).findall(content)
  if match:
    xbmc.executebuiltin('XBMC.Notification(Info:,'+match[0].strip()+',15000)')
  else:
    debug("playVideoUrl url2: "+baseUrl+"/play/media/"+videoID+"?devicetype=pc&features=flash")
    content = getUrl(baseUrl+"/play/media/"+videoID+"?devicetype=pc&features=flash")
    decoded = json.loads(content)
    try:
      subtitleUrl = decoded['_subtitleUrl']
      subtitleOffset = decoded['_subtitleOffset']
    except:
      subtitleUrl = False
    #debug("playVideoUrl subtitleUrl: "+ subtitleUrl)
    mediaArrays = decoded['_mediaArray']
    streamType = False
    savedQuality = -1
    replacementQuality = 0
    i = 0
    for mediaArray in mediaArrays:
      mediaStreamArrays = decoded['_mediaArray'][i]['_mediaStreamArray']
      j = 0
      for entry in mediaStreamArrays:
        stream = decoded['_mediaArray'][i]['_mediaStreamArray'][j]['_stream']
        quality = decoded['_mediaArray'][i]['_mediaStreamArray'][j]['_quality']
        if quality == 'auto' and i == 0 and j == 0:
          if stream.endswith('.smil'):
            url = stream
            streamType = 'smil'
          else:
            url = stream
            streamType = 'f4m'
        else:
          streamType = 'httprtmp'
          if isinstance(stream, list):
            stream = stream[0]
          if '_server' in decoded['_mediaArray'][i]['_mediaStreamArray'][j] and decoded['_mediaArray'][i]['_mediaStreamArray'][j]['_server'] != '':
            if mdrHd:#MDR HD "hack"
              replacementUrl = stream.split('/')[-1]
              replacementQuality = int(quality)
            stream = decoded['_mediaArray'][i]['_mediaStreamArray'][j]['_server']+" playpath="+stream+" live=true"
          elif mdrHd and 'http://ondemand.mdr.de' in stream and replacementQuality == int(quality):#MDR HD "hack"
            try:
              stream = stream.replace(stream.split('/')[-1],replacementUrl)
            except:
              pass
          if int(quality) > savedQuality and int(quality) <= videoQuality:
            url = stream
        j += 1
      i += 1

    if streamType == 'smil':
      content = getUrl(url)
      match = re.compile('<meta base="(.+?)".+?<video src="(.+?)"', re.DOTALL).findall(content)
      url = match[0][0]+match[0][1]
      streamType = 'f4m'
    if streamType == 'f4m':
      #f4mproxy.f4mProxyHelper().playF4mLink(url,'TODO')
      url = url.replace('/z/','/i/').replace('manifest.f4m','master.m3u8').replace('cdn-vod-hds.br.de','cdn-vod-ios.br.de')
      streamType = 'httprtmp'
      """
      from f4mproxy import f4mProxyHelper
      f4mHelper=f4mProxyHelper()
      name = 'TODO'
      url += '?g='+char_gen(12)+'&hdcore=3.4.0&plugin=aasp-3.4.0.132.66'
      resolved_url,f4mProxyStopEvent = f4mHelper.start_proxy(url, name)
      listitem = xbmcgui.ListItem(path=resolved_url)
      xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
      """
    if streamType == 'httprtmp':
      listitem = xbmcgui.ListItem(path=url)
      if showSubtitles and subtitleUrl and helix:
        subtitle.setSubtitle(subtitleUrl,True,subtitleOffset)
        listitem.setSubtitles(subFile)
      xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
      if showSubtitles and subtitleUrl and not helix:
        subtitle.setSubtitle(subtitleUrl,False,subtitleOffset)


def queueVideo(url, name):
  playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
  listitem = xbmcgui.ListItem(name)
  playlist.add(url, listitem)


def playLive(liveID):
  content = getUrl(baseUrl+"/tv/live?kanal="+liveID)
  match = re.compile('/play/media/(.+?)&', re.DOTALL).findall(content)
  playVideo(match[0])


def playLiveARD():
  content = getUrl("http://live.daserste.de/de/livestream.xml")
  match = re.compile('<asset type=".*?Live HLS">.+?<fileName>(.+?)</fileName>', re.DOTALL).findall(content)
  url = ""
  if match:
    url = match[0]
  if url:
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)



def search():
  keyboard = xbmc.Keyboard('', translation(30008))
  keyboard.doModal()
  if keyboard.isConfirmed() and keyboard.getText():
    search_string = keyboard.getText().replace(" ", "+")
    listVideos(baseUrl+"/tv/suche?searchText="+search_string)


def cleanTitle(title):
  title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#034;", "\"").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
  title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace("&eacute;", "é").replace("&egrave;", "è")
  title = title.replace("&#x00c4;","Ä").replace("&#x00e4;","ä").replace("&#x00d6;","Ö").replace("&#x00f6;","ö").replace("&#x00dc;","Ü").replace("&#x00fc;","ü").replace("&#x00df;","ß")
  title = title.replace("&apos;","'").strip()
  return title

def char_gen(size=1, chars=string.ascii_uppercase):
  return ''.join(random.choice(chars) for x in range(size))

def getUrl(url):
  print 'get: '+url
  req = urllib2.Request(url)
  req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
  response = urllib2.urlopen(req)
  link = response.read()
  response.close()
  return link


def favs(param):
  mode = param[param.find("###MODE###=")+11:]
  mode = mode[:mode.find("###")]
  channelEntry = param[param.find("###TITLE###="):]
  if mode == "ADD":
    if os.path.exists(channelFavsFile):
      fh = open(channelFavsFile, 'r')
      content = fh.read()
      fh.close()
      if content.find(channelEntry) == -1:
        fh = open(channelFavsFile, 'a')
        fh.write(channelEntry+"\n")
        fh.close()
    else:
      fh = open(channelFavsFile, 'a')
      fh.write(channelEntry+"\n")
      fh.close()
  elif mode == "REMOVE":
    refresh = param[param.find("###REFRESH###=")+14:]
    refresh = refresh[:refresh.find("#")]
    fh = open(channelFavsFile, 'r')
    content = fh.read()
    fh.close()
    entry = content[content.find(channelEntry):]
    fh = open(channelFavsFile, 'w')
    fh.write(content.replace(channelEntry+"\n", ""))
    fh.close()
    if refresh == "TRUE":
      xbmc.executebuiltin("Container.Refresh")


def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict


def addLink(name, url, mode, iconimage, duration="", desc="", genre='',title=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  if title!="":
    u=u+"&title="+title
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  #liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration, "Plot": desc, "Genre": genre})
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  #liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok


def addDir(name, url, mode, iconimage, desc="", nextPage=False, einsLike=False,title=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  if title!="":
    u=u+"&title="+title  
  if nextPage:
    u += "&nextpage=True"
  if einsLike:
    u += "&einslike=True"
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok


def addShowDir(name, url, mode, iconimage, showName=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&name="+urllib.quote_plus(name)+"&mode="+str(mode)+"&nextpage=True"+"&hideshowname=True"+"&showName="+urllib.quote_plus(showName)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
  #liz.addContextMenuItems([(translation(30028), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok


def addShowFavDir(name, url, mode, iconimage):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
  #liz.addContextMenuItems([(translation(30029), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok



params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
title = urllib.unquote_plus(params.get('title', ''))
showName = urllib.unquote_plus(params.get('showName', ''))
hideShowName = urllib.unquote_plus(params.get('hideshowname', '')) == 'True'
nextPage = urllib.unquote_plus(params.get('nextpage', '')) == 'True'
einsLike = urllib.unquote_plus(params.get('einslike', '')) == 'True'

if mode == 'listVideos':
  listVideos(url)
if mode == 'listVideosXml':
  listVideosXml(url)
elif mode == 'listDirRss':
  listDirRss(url)
elif mode == 'listVideosRss':
  listVideosRss(url,showName,hideShowName,nextPage,einsLike)
elif mode == 'listChannelVideos':
  listChannelVideos(url)
elif mode == 'listEinsLike':
  listEinsLike()
elif mode == 'listFootball':
  listFootball()
elif mode == 'listShowsFavs':
  listShowsFavs()
elif mode == 'listChannel':
  listChannel(url)
elif mode == 'listChannels':
  listChannels()
elif mode == 'listLiveChannels':
  listLiveChannels()
elif mode == 'listShowsAZMain':
  listShowsAZMain()
elif mode == 'listShowsAZ':
  listShowsAZ(url)
elif mode == 'listCats':
  listCats(url)
elif mode == 'playVideo':
  playVideo(url)
elif mode == 'playVideoUrl':
  playVideoUrl(url)
elif mode == "queueVideo":
  queueVideo(url, name)
elif mode == 'playLiveARD':
  playLiveARD()
elif mode == 'playLive':
  playLive(url)
elif mode == 'search':
  search()
elif mode == 'favs':
  favs(url)
elif mode == 'listfilesofshow':
  listfilesofshow(url,title)
else:
  index()
