#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
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


xbmcplugin.setContent(addon_handle, 'movies')

baseurl="http://www.tlc.de"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


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
    

  
def addDir(name, url, mode, thump, desc="",page=1,nosub=0,iddpost="",idd=""):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&nosub="+str(nosub)+"&iddpost="+str(iddpost)+"&idd="+str(idd)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
  liz.setArt({ 'banner' : icon })
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, thump, duration="", desc="", genre='',director="",bewertung=""):
  debug("URL ADDLINK :"+url)
  debug( icon  )
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name,thumbnailImage=thump)
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre, "Director":director,"Rating":bewertung})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
	#xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict


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
        cj.save(cookie,ignore_discard=True, ignore_expires=True)               
        return content


    

   
   

  
def liste():  
    addDir("Settings","Settings","Settings","")
    addDir("Alle Serien","http://www.tlc.de/videos/","list_buchstaben","")
    
    xbmcplugin.endOfDirectory(addon_handle) 

  
def playvideo(url):          
    content=geturl(url)
    htmlPage = BeautifulSoup(content, 'html.parser')      
    element = htmlPage.find("object",attrs={"class":"BrightcoveExperience"})  
    debug(element)
    params = element.find_all("param")
    searchstring=""
    urls="https://c.brightcove.com/services/viewer/htmlFederated?"
    for param in params:
       name=param["name"]
       value=param["value"]       
       searchstring=searchstring+"&"+urllib.quote_plus(name)+"="+urllib.quote_plus(value)
    urls=urls+searchstring
    content=geturl(urls)
    quellen  = re.compile('"defaultURL":"(.+?)","encodingRate":(.+?),', re.DOTALL).findall(content)
    br=0
    video=""
    for quelle,bitrate in quellen:
       if br < bitrate:
          br=bitrate
          video=quelle.replace("\\/","/")       
    listitem = xbmcgui.ListItem(path=video)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
       
    
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page = urllib.unquote_plus(params.get('page', ''))
nosub= urllib.unquote_plus(params.get('nosub', ''))
iddpost=urllib.unquote_plus(params.get('iddpost', ''))
idd=urllib.unquote_plus(params.get('idd', ''))

  
def  list_buchstaben(url):
    content=geturl(url)
    htmlPage = BeautifulSoup(content, 'html.parser')  
    subrubrikl = htmlPage.find("ul",attrs={"class":"slides"})    
    elemente = subrubrikl.find_all("a")    
    iddpost = htmlPage.find("input",attrs={"id":re.compile("^dni_listing_post_id")})["value"]    
    idd = htmlPage.find_all("div",attrs={"id":re.compile("^dni-listing-module-")})[-1]["data-id"]    
    for element in elemente:
       debug(element)
       linkurl = url+element["href"]
       title = element.text
       addDir(title,title,"list_buchstabe","",iddpost=iddpost,idd=idd,page=1)      
    xbmcplugin.endOfDirectory(addon_handle)      
    
def list_buchstabe(url,iddpost,idd,page=1):
   if url=="All Pages":
     zusatz=""
   else:
      zusatz="letter="+url+"&"   
   newurl="http://www.tlc.de/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&"+zusatz+"page="+str(page)+"&id="+str(idd)+"&post_id="+iddpost+"&view_type=grid"
   debug(newurl)
   content=geturl(newurl)
   struktur = json.loads(content)        
   total=struktur["total_pages"]
   curr=struktur["current_page"]
   codee=struktur["html"]
   htmlPage = BeautifulSoup(codee, 'html.parser')      
   elemente = htmlPage.find_all("a")    
   for element in elemente:
       link=element["href"]       
       debug(link)
       title=element.find("h3").text.encode("utf-8")
       debug(title)
       image=element.find("img")["src"]
       debug(image)
       if "pagetype-video" in element["class"]:
          addLink(title,link,"list_staffeln",image)          
       else:
          addDir(title,link,"list_staffeln",image)              
   if int(curr)<int(total):
      addDir("Next",url,"list_buchstabe","",iddpost=iddpost,idd=idd,page=int(page)+1)      
   xbmcplugin.endOfDirectory(addon_handle)       

def list_staffeln(url):
    wegtitle=["online sehen","ALLE STAFFELN","Rezepte"]
    content=geturl(url)
    htmlPage = BeautifulSoup(content, 'html.parser')      
    elemente = htmlPage.find_all("div",attrs={"class":re.compile("^cfct-module dni")})        
    for i in range(1,len(elemente)):
        element=elemente[i]
        debug(element)
        try:
            title=element.find("div",attrs={"class":re.compile("^tab-module-header")}).text.encode("utf-8")
        except:
            try:
                    title=element.find("h2").text.encode("utf-8")
            except:
                 title=""
        if not title=="":   
            debug("###"+title+"###")            
            weg=0
            for wegstring in wegtitle:             
              if wegstring in title: 
                weg=1
                break
            if weg==0:
                addDir(title,url,"list_rubrik","",nosub=title)     
    subrubrik = htmlPage.find("div",attrs={"class":re.compile("^normal no-desc")})        
    debug(subrubrik)
    try:
        elemente = subrubrik.find_all("a")        
        for i in range(0,len(elemente)):
            element=elemente[i]
            debug("#####")
            debug(element)
            link=element["href"]
            image = element.find("img")["src"]
            title = element.find("h3").text.encode("utf-8")
            if not title=="":               
                weg=0
                for wegstring in wegtitle:             
                    if wegstring in title: 
                        weg=1
                        break
                if weg==0:                
                    addDir(title,link,"list_rubrik",image,nosub=title)
    except:
        pass
    xbmcplugin.endOfDirectory(addon_handle)        

def  list_rubrik(url,nosub):
    debug("---> "+url)
    content=geturl(url)
    htmlPage = BeautifulSoup(content, 'html.parser')     
    #                                                 <div class="cfct-module dni-content-slider-theme">
    #<input id="dni_listing_post_id_31446b" type="hidden" value="64499"/>    
    elemente = htmlPage.find_all("div",attrs={"class":re.compile("^cfct-module dni")})  
    idd=""
    debug("Nosub :"+nosub)
    for i in range(0,len(elemente)):  
        element=elemente[i] 
        debug(element)
        if nosub in element.text.encode("utf-8"):
            elemente2 = element.find_all("li",attrs={"class":re.compile("^pagetype-video")})   
            xx=1
            if len(elemente2)<=0:
              elemente2 = element.find_all("a")   
              xx=0
            for element2 in elemente2:              
              debug(element2)
              try:
                    type=element2["class"]
              except:
                     type=""
              try:
                if xx==1:
                   element2=element2.find("a")
                link=element2["href"]
                image = element2.find("img")["src"]
                title = element2.find("h3").text.encode("utf-8")
                if "pagetype-video" in type:
                    addLink(title,link,"playvideo",image)
                else:
                    addDir(title,link,"list_staffeln",image,nosub=title)
                debug(element)
              except:
                 pass
            #break
    try:
      element = htmlPage.find("a",attrs={"class":re.compile("^button-next")})
      blub= element["href"]     
      iddpost = htmlPage.find("input",attrs={"id":re.compile("^dni_listing_post_id")})["value"]    
      idd = htmlPage.find_all("div",attrs={"id":re.compile("^dni-listing-module-")})[-1]["data-id"]  
      addDir("Next",url,"list_buchstabe","",iddpost=iddpost,idd=idd,page=2)      
    except: 
       pass    
    xbmcplugin.endOfDirectory(addon_handle)        
        





# Haupt Menu Anzeigen     
if mode is '':
     liste()   
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'playvideo':
          playvideo(url) 
  if mode == 'list_buchstabe':
          list_buchstabe(url,iddpost,idd,page)
if mode == 'list_buchstaben':
          list_buchstaben(url)
if mode == 'list_staffeln':
          list_staffeln(url)          
if mode == 'list_rubrik':
          list_rubrik(url,nosub)            