#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import os
import re
import xbmcplugin
import xbmcaddon,xbmc,xbmcvfs,shutil
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

base_url="http://www.zeeone.de"

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)
cookie=os.path.join( temp, 'cookie.jar')
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)                  


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
        #cj.save(cookie,ignore_discard=True, ignore_expires=True)               
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
  url=base_url+"/BollyThek"
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')
  elemente = htmlPage.find_all("a",attrs={"class":" dropdown-toggle"})  
  for element in elemente:
      addDir(element.text.encode("utf-8"),element["href"].encode("utf-8"),"thema","")  
  xbmcplugin.endOfDirectory(pluginhandle)

def thema(urls):
  url=base_url+urls
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')
  # <ul class="dropdown-menu mega-dropdown-menu row">
  elemente = htmlPage.find_all("li",attrs={"class":"dropdown mega-dropdown"})    
  for element in elemente:
     if urls in str(element):
        links=element.find_all("a")
        for link in links:
         try:
          text_url=link.text.encode("utf-8")
          link_url=link["href"].encode("utf-8")
          lurl=re.compile('ProgramUrlName=(.+)', re.DOTALL).findall(link_url)[0]    
          link_url=urls+"?ProgramUrlName="+lurl
          debug("link_url :"+link_url)
          addDir(text_url,link_url.encode("utf-8"),"serie","")
         except:
            debug("ERR")
            debug(link)
  addDir("Alle",urls,"serie","")
  xbmcplugin.endOfDirectory(pluginhandle)          
     

def serie(url):
   url=base_url+url
   content=geturl(url)
   htmlPage = BeautifulSoup(content, 'html.parser')
   elemente = htmlPage.find_all("div",attrs={"class":"carouselbox"})  
   for element in elemente:
      debug("+++++")
      link=element.find("a")["href"].encode("utf-8")
      img=element.find("img")["data-lazy"].encode("utf-8")
      title=element.find("h3").text.encode("utf-8")
      folge=element.find("span").text.encode("utf-8").replace("Folge ","")        
      datum=element.find("p",attrs={"class":"pg-date"}).text.encode("utf-8")
      if int(folge)>0 :
         title =title + " Folge: "+folge
      title=title+ " ( "+datum + " )"
      addLink(title,link,"Play",img)
      debug(folge)
   xbmcplugin.endOfDirectory(pluginhandle)
   
  
def Play(surl):
    url=base_url+surl
    debug("Play url: "+url)
    content = requests.get(url,allow_redirects=False,verify=False,cookies=cj).text.encode('utf-8')
    #debug(content)
    urln=re.compile('file: [\'"]([^"\']+)[\'"]', re.DOTALL).findall(content)[0]    
    listitem = xbmcgui.ListItem(path=urln)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

    
if mode == "":
    index()
if mode == "thema":
     thema(url)
if mode == "serie":
     serie(url)     
if mode == "Play":
     Play(url)
