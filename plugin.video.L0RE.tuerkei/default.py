#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import os
import re
import xbmcplugin
import xbmcaddon,xbmc
import xbmcgui,json,cookielib
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString

cj = cookielib.LWPCookieJar();

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def getUrl(url,data="x",header=""):
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]
        else:
          opener.addheaders = header       
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #debug( e.code   )
             cc=e.read()
             debug("Error : " +cc)

        opener.close()
        return content      


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, duration="", desc="", genre='',text=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name"+urllib.quote_plus(name)+"&text="+urllib.quote_plus(text)+"&bild="+iconimage
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", defaultBackground)
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok

def addDir(name, url, mode, iconimage, desc="",text="",page=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&text="+str(text)+"&page="+str(page)+"&name"+str(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
page = urllib.unquote_plus(params.get('page', ''))

def index():  
  #ListRubriken("http://"+language2+".euronews.com","",x=1)
  addDir("Alle Sender","https://www.canlitvizle.com/tum-kanallar","allsender","")

  xbmcplugin.endOfDirectory(pluginhandle)  
  

def Play(url):
    debug("Play url: "+url)
    content = getUrl(url)  
    htmlPage = BeautifulSoup(content, 'html.parser')
    #debug(content)
    iframe_tag = htmlPage.find("div",attrs={"class":"player-inner"})    
    iframe=iframe_tag.find("iframe")
    nurl=iframe["src"]    
    header=[]
    header.append (("User-Agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"))
    header.append (("Referer",url))
    content = getUrl(nurl,header=header)
    video=re.compile("file: '(.+?)',", re.DOTALL).findall(content)[0]                		
    headerfelder="user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36&Referer="+nurl
    listitem = xbmcgui.ListItem(path=video+"|"+headerfelder)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    
def allsender(url):
   content = getUrl(url)
   debug("##")
   debug(content)
   htmlPage = BeautifulSoup(content, 'html.parser')
   subtree = htmlPage.find("div",attrs={"class":"tv-inner"})
   elemente = subtree.find_all("a")
   for element in elemente:     
     link=element["href"]
     img=""
     title=element["title"].encode("utf-8")    
     addLink(title ,link,"Play",img)
   xbmcplugin.endOfDirectory(pluginhandle) 
   
if mode == "":
    index()
if mode == "allsender":
     allsender(url)
if mode == "Play":
     Play(url)
