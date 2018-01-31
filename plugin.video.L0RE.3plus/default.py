#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil, json
import time
import base64
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).decode('utf-8')
profile = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
temp       = xbmc.translatePath(os.path.join(profile, 'temp', '')).decode("utf-8")
fanart = os.path.join(addonPath, 'fanart.jpg').decode('utf-8')
icon = os.path.join(addonPath, 'icon.png').decode('utf-8')
pic = os.path.join(addonPath, 'resources/media/')
baseURL = "http://3plus.tv"

xbmcplugin.setContent(addon_handle, 'movies')
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

cachezeit=addon.getSetting("cachetime")   
cache = StorageServer.StorageServer("plugin.video.L0RE.3plus", cachezeit) # (Your plugin name, Cache time in hours

try:
    if xbmcvfs.exists(temp):
        shutil.rmtree(temp)
except: pass
xbmcvfs.mkdirs(temp)
cookie=os.path.join( temp, 'cookie.jar')
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie, ignore_discard=True, ignore_expires=True)                  

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def geturl(url,data="x",header="",referer=""):
    global cj
    debug("Get Url: " +url)
    for cook in cj:
        debug(" Cookie :"+ str(cook))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    if header=="":
        opener.addheaders = [('User-Agent', userAgent)]
    else:
        opener.addheaders = header 
    if not referer=="":
        opener.addheaders = [('Referer', referer)]
    try:
        if data!="x" :
            content=opener.open(url,data=data).read()
        else:
            content=opener.open(url).read()
    except urllib2.HTTPError as e:
        #debug( e.code )  
        cc=e.read()  
        debug("Error : " +cc)
        content=""
    opener.close()
    cj.save(cookie, ignore_discard=True, ignore_expires=True)
    return content

def Serien():
    content = cache.cacheFunction(geturl,'http://3plus.tv/videos') 
    htmlPage = BeautifulSoup(content, 'html.parser')  
    Videos_block = htmlPage.find("div",attrs={"class":"view view-videos view-id-videos view-display-id-block_8 view-dom-id-4"}) 
    Videos = Videos_block.find_all("li") 
    for video in Videos:
        linkhtml=video.find("a")
        link= baseURL+linkhtml["href"]
        bild = pic+linkhtml["href"].lower().replace('/videos/', '')+'.jpg'
        title = linkhtml.text
        addDir(title,link,"staffelliste",bild)
    xbmcplugin.endOfDirectory(addon_handle)

def staffelliste(url):
    content = cache.cacheFunction(geturl,url)
    htmlPage = BeautifulSoup(content, 'html.parser')  
    Videos = htmlPage.find_all("div",attrs={"class":"views-field-title-1"})
    for video in Videos:
        linkhtml=video.find("a")
        link= baseURL+linkhtml["href"]
        bild = pic+linkhtml["href"].lower().split('/')[2].replace('/videos/', '')+'.jpg'
        title = linkhtml.text
        addDir(title,link,"staffelreload",bild)
    xbmcplugin.endOfDirectory(addon_handle)

def staffelreload(url):
    YearCode = ('Staffel 2007','Staffel 2008','Staffel 2009','Staffel 2010','Staffel 2011','Staffel 2012','Staffel 2013','Staffel 2014','Staffel 2015','Staffel 2016','Staffel 2017','Staffel 2018','Staffel 2019','Staffel 2020','Staffel 2021','Staffel 2022')
    content = cache.cacheFunction(geturl,url) 
    htmlPage = BeautifulSoup(content, 'html.parser')  
    Videos = htmlPage.find_all("div",attrs={"class":"views-field-title-1"})
    for video in Videos:
        linkhtml=video.find("a")
        link= baseURL+linkhtml["href"]
        bild = pic+linkhtml["href"].lower().split('/')[2].replace('/videos/', '')+'.jpg'
        title = linkhtml.text
        if not title in YearCode and not 'Trailer' in title:
            addDir(title,link,"episoden",bild)
    xbmcplugin.endOfDirectory(addon_handle)

def episoden(url):
    #views-field-field-video-embed
    debug("Start episodes")
    debug(url)
    videoIsolated = set()
    content = geturl(url)
    htmlPage = BeautifulSoup(content, 'html.parser')
    nextPage = htmlPage.find("h2",attrs={"class":"pane-title"})
    subhtml = htmlPage.find("div",attrs={"class":"pane-content"})
    Videos = subhtml.find_all("li",attrs={"class":re.compile("views-row")})
    for video in Videos:
        debug("------")
        debug(video)
        linkrhtml=video.find("div",attrs={"class":"views-field-field-threeq-value"})
        debug(linkrhtml)
        link=linkrhtml.find("div",attrs={"class":"field-content"}).text
        debug("######"+link+"######")    
        titlehtml=video.find("div",attrs={"class":"views-field-title"})
        title=titlehtml.find("div",attrs={"class":"field-content"}).text
        if title in videoIsolated:
            continue
        videoIsolated.add(title)
        bild=video.find("img")["src"]
        bild=bild.replace("_video","_big")
        addLink(title,link,"playvideo",bild)
    xbmcplugin.endOfDirectory(addon_handle)

def playvideo(url):
    newurl="http://playout.3qsdn.com/"+url+"?timestamp=0&autoplay=false&key=0&js=true&container=sdnPlayer&width=100%&height=100%&protocol=http&vastid=0&playlistbar=false"
    ref="http://playout.3qsdn.com/"+url   
    debug(newurl)
    content=geturl(newurl)   
    content=content.replace("\\x2D","-")
    liste=re.compile("{src:'(.+?)', type: '(.+?)', quality: '(.+?)'", re.DOTALL).findall(content)
    quality_setting=addon.getSetting("quality")
    stream=""
    for url,type,quality in liste:     
        stream=url
        if quality==quality_setting:
            break     
    if stream=="":
        token2=re.compile("sdnPlayoutId:'(.+?)'", re.DOTALL).findall(content)[0]
        url2="http://playout.3qsdn.com/"+token2+"?timestamp=0&key=0&js=true&autoplay=false&container=sdnPlayer_player&width=100%25&height=100%25&protocol=http&token=0&vastid=0&jscallback=sdnPlaylistBridge"
        content=geturl(url2)   
        debug("url2 :"+url2)
        liste=re.compile("{src:'(.+?)', type: '(.+?)', quality: '(.+?)'", re.DOTALL).findall(content)   
        for url,type,quality in liste:
            debug(quality)
            debug(url)
            stream=url
            if quality==quality_setting:
                break
    listitem = xbmcgui.ListItem(path=stream)   
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

def addDir(name, url, mode, thump, desc="", page=1, sub=""):   
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&sub="+str(sub)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'fanart' : thump })
    liz.setArt({'thumb' : thump })
    liz.setArt({'banner' : icon })
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
  
def addLink(name, url, mode, thump, duration="", desc="", genre='', director="", bewertung=""):
    debug("URL ADDLINK :"+url)
    debug(icon)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name,thumbnailImage=thump)
    liz.setArt({'fanart' : fanart})
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre, "Director": director, "Rating": bewertung})
    liz.setProperty('IsPlayable', 'true')
    liz.addStreamInfo('video', {'duration' : duration})
    #xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page= urllib.unquote_plus(params.get('page', ''))
sub= urllib.unquote_plus(params.get('sub', ''))


    # Wenn Settings ausgewählt wurde
if mode == 'Settings':
    addon.openSettings()
    # Wenn Kategory ausgewählt wurde
elif mode == 'staffelliste':
    staffelliste(url)
elif mode == 'staffelreload':
    staffelreload(url)
elif mode == 'episoden':
    episoden(url)
elif mode == 'playvideo':
    playvideo(url)
    # Haupt Menü Anzeigen 
else:
    Serien()