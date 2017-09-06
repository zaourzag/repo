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
from django.utils.encoding import smart_str

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
  addDir("Drama","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Drama&pageType=BollyThek","newlist","",page=1)
  addDir("Action","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Action&pageType=BollyThek","newlist","",page=1)
  addDir("Liebe","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Liebe&pageType=BollyThek","newlist","",page=1)
  addDir("Komödie","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Komödie&pageType=BollyThek","newlist","",page=1)
  addDir("Familie","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Familie&pageType=BollyThek","newlist","",page=1)
  addDir("Kino","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Kino&pageType=BollyThek","newlist","",page=1)
  addDir("Serie","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Serie&pageType=BollyThek","newlist","",page=1)
  addDir("Musik","http://www.zeeone.de/Handlers/GenreLazyLoadHandler.ashx?genre=Musik&pageType=BollyThek","newlist","",page=1)
  xbmcplugin.endOfDirectory(pluginhandle)  
  

def Play(url):
    debug("Play url: "+url)
    content = requests.get(url,allow_redirects=False,verify=False,cookies=cj).text.encode('utf-8')
    #debug(content)
    urln=re.compile('file: [\'"]([^"\']+)[\'"]', re.DOTALL).findall(content)[0]    
    listitem = xbmcgui.ListItem(path=urln)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

    
def newlist(url,page=1):
   nurl=url +"&page="+str(page)
   debug("newlist url :"+nurl)   
   content = requests.get(nurl,allow_redirects=False,verify=False,cookies=cj).text.encode('utf-8')
   debug("##")
   debug(content)
   htmlPage = BeautifulSoup(content, 'html.parser')
   elemente = htmlPage.find_all("article")
   for element in elemente:
     debug("####")
     link=smart_str(element.find("a")["href"])
     img=element.find("img")["src"]
     name=smart_str(element.find("h3",attrs={"class":"pg-name"}).text)
     folge=smart_str(element.find_all("span")[1].text)     
     if not folge=="Folge 0":
        endn=name+ " "+folge
     else:
        endn=name
     addLink(endn ,"http://www.zeeone.de"+link,"Play",img)
   addDir("Next",url,"newlist","",page=str(int(page)+1))
   xbmcplugin.endOfDirectory(pluginhandle) 
   
if mode == "":
    index()
if mode == "newlist":
     newlist(url,page)
if mode == "Play":
     Play(url)
