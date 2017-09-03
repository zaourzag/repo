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
import xbmcgui,json
import pyxbmct,time
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
from django.utils.encoding import smart_str

addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString

while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))):
    addon.openSettings()

language = addon.getSetting("language")
languages = ["en", "gr", "fr", "de", "it", "es", "pt", "pl", "ru", "ua", "tr", "ar", "pe"]
language = languages[int(language)]
language2 = language.replace("en", "www").replace("pe", "persian").replace("ar", "arabic")

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def artikeltext(text):
#
    text=text.replace ("</p>","").replace("<p>","").replace("<div id='articleTranscript'>","").replace("<br />","").replace('<div id="image-caption">',"").replace("	","").replace("<p","")
    text=text.replace ("<em>","").replace("</em>","")
    text=text.replace ("<h3>","").replace("</h3>","")
    text=text.replace ("<hr>","")
    text = text.replace("&quot;", "\"")
    text = text.replace("&apos;", "'")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&laquo;", "<<")
    text = text.replace("&raquo;", ">>")
    text = text.replace("&#039;", "'")
    text = text.replace("&#8220;", "\"")
    text = text.replace("&#8221;", "\"")
    text = text.replace("&#8211;", "-")
    text = text.replace("&#8216;", "\'")
    text = text.replace("&#8217;", "\'")
    text = text.replace("&#9632;", "")
    text = text.replace("&#8226;", "-")
    text = text.replace('<span class="caps">', "")
    text = text.replace('</span>', "")
    text = text.replace('\u00fc', "ü")  
    text = text.replace('\u00e4', "ä")     
    text = text.replace('\u00df', "ß")      
    text = text.replace('\u00f6', "ö")      
    text = text.replace('\/', "/")    
    #text = text.replace('\n', "")    
    text = text.strip()
    return text
    
class Infowindow(pyxbmct.AddonDialogWindow):
    bild=""
    nur_bild=""
    text=""
    pos=0
    def __init__(self, title='',text='',image='',nurbild=0):
        super(Infowindow, self).__init__(title)
        self.setGeometry(600,600,8,8)
        self.bild=image
        self.nur_bild=nurbild
        self.text=text        
        self.set_info_controls()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_info_controls(self):
      self.textbox=pyxbmct.TextBox()  
      self.image = pyxbmct.Image(self.bild)           
      if self.nur_bild==0:
        self.placeControl(self.image, 0, 0,columnspan=2,rowspan=2)
        self.placeControl(self.textbox, 2, 0, columnspan=8,rowspan=6)                  
      else:
        self.placeControl(self.image, 0, 0,columnspan=8,rowspan=6)
        #self.placeControl(self.textbox, 6, 0,columnspan=8,rowspan=2)     
      self.textbox.setText(self.text)
      self.connectEventList(
             [pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_UP],
            self.hoch)         
      self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN],
            self.runter)                  
      self.setFocus(self.textbox)            
    def hoch(self):
        self.pos=self.pos-1
        if self.pos < 0:
          self.pos=0
        self.textbox.scroll(self.pos)
    def runter(self):
        self.pos=self.pos+1        
        self.textbox.scroll(self.pos)
        posnew=self.textbox.getPosition()
        debug("POSITION : "+ str(posnew))
              

#       window = Infowindow(title=title_artikel,text=text,image=bild,nurbild=nurbild)
#       window.doModal()
 #      del window
       

def cleanTitle(title):
    return title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#038;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&#8211;", "-").replace("&#8220;", "-").replace("&#8221;", "-").replace("&#8217;", "'").replace("&#8230;", "…").replace("&quot;", "\"").strip()


def getUrl(url, data=None, cookie=None):
    debug("URL :" + url)
    if data != None:
        req = urllib2.Request(url, data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    else:
        req = urllib2.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    if cookie != None:
        req.add_header('Cookie', cookie)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


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

def addDir(name, url, mode, iconimage, desc="",text="",offset=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&text="+str(text)+"&offset="+str(offset)+"&name"+str(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
text = urllib.unquote_plus(params.get('text', ''))
name = urllib.unquote_plus(params.get('name', ''))
bild = urllib.unquote_plus(params.get('bild', ''))
offset = urllib.unquote_plus(params.get('offset', ''))

 
def playLive():    
    url="http://fr-par-iphone-1.cdn.hexaglobe.net/streaming/euronews_ewns/iphone_"+language+".m3u8"
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

  
def Rubriken(urls):
   debug("Rubriken urls :"+urls)
   content = getUrl(urls)     
   htmlPage = BeautifulSoup(content, 'html.parser')
   elemente = htmlPage.find_all("a",attrs={'class':'enw-menuList__sub-title'})
   anz=0
   liste=[]
   for element in elemente:
      if not element.text.strip() in liste:
        if not element.text.strip()=="Video" and not element.text.strip()=="Living It":
            debug(element["href"])
            addDir(element.text.strip(), element["href"], 'Rubrik', "", "",text=str(anz))           
            liste.append(element.text.strip())
      anz+=1   

      
def SubRubriken(urls):
   debug("Rubriken urls :"+urls)
   if not "http:" in urls:
      newurl="http://"+language2+".euronews.com"+urls
   else: 
      newurl=urls
   content = getUrl(newurl)     
   htmlPage = BeautifulSoup(content, 'html.parser')
   elemente = htmlPage.find_all("div",attrs={'class':"medium-2 columns"})   
   anz=0
   liste=[]
   for element in elemente:
      linkmain=element.find("a",attrs={"class":"enw-menuList__sub-title"})["href"]
      if urls in linkmain:
          debug("Gefunden")
          elemente2=element.find_all("a",attrs={'class':"enw-menuList__sub-item"})   
          for element2 in elemente2:
              print (element2)
              print("#####")
              title=element2.text.strip().encode('utf-8')
              if not element2.text.strip() in liste:
                try:
                    match=re.compile('/(.+?)/(.+)', re.DOTALL).findall(element2["href"])
                    debug(match)                
                    urlt="/"+match[0][1]
                    addDir(element2.text.strip().encode('utf-8'), "/api/program"+ urlt, 'Seite', "", "",text=str(anz))           
                    liste.append(element2.text.strip())
                    anz+=1   
                except:
                    pass
   try:                
    link=re.compile('data-api-url="(.+?)"', re.DOTALL).findall(content)[0]
    addDir("Artikel", link, 'Seite', "",offset=1)           
   except:
     pass
   #GET http://www.euronews.com/api/theme/culture?offset=16&extra=1                
   return anz
   
def Seite(url,offset=1):
  debug("URL :"+url)
  urln="http://"+language2+".euronews.com"+url+"?offset="+str(offset)+"&extra=1"
  content = getUrl(urln)  
  struktur = json.loads(content)
  for artikel in struktur["articles"]:
        debug(artikel)
        title=smart_str(artikel["title"])
        bild=artikel["images"][0]["url"].replace("{{w}}x{{h}}","800x800")
        videourlhd=""
        videourlmd=""
        if  str(artikel["video"]) =="1":
            for video in artikel["videos"] :
                debug(video)
                if video["quality"]=="hd":
                    try:
                        videourlhd=video["url"]
                    except:
                        pass
                if  video["quality"]=="md":#
                    videourlmd=video["url"]
            debug("Title :"+title)            
            addLink(title,videourlhd,"Play",bild)
        else:
            addLink("TXT: "+title.decode('ascii', 'ignore'),"","infofenster",bild,text=smart_str(artikel["plainText"]))
        # pass
  debug(struktur["extra"]["offset"])
  debug(struktur["extra"]["total"])
  debug(struktur["extra"]["count"])
  if struktur["extra"]["offset"]< struktur["extra"]["total"]:
     addDir("next", url, 'Seite', "",offset=struktur["extra"]["offset"]+struktur["extra"]["count"])           
  xbmcplugin.endOfDirectory(pluginhandle)   
  
def Rubrik(url):
   debug("Rubrik urls :"+url)   
   anz=SubRubriken(url)
   xbmcplugin.endOfDirectory(pluginhandle)   
   
def index():  
  #ListRubriken("http://"+language2+".euronews.com","",x=1)
  addLink("Live","","playlive","")
  Rubriken("http://"+language2+".euronews.com")  
  xbmcplugin.endOfDirectory(pluginhandle)   

def  Play(url):  
  listitem = xbmcgui.ListItem(path=url)
  xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)  
  
def infofenster(title_artikel,text,bild):
    window = Infowindow(title=title_artikel,text=text,image=bild,nurbild=0)
    window.doModal()
    del window

def playlive():
  url="http://www.euronews.com/api/watchlive.json"
  content = getUrl(url)   
  urln=re.compile('"url":"(.+?)"', re.DOTALL).findall(content)[0]
  urln=urln.replace("\/","/")  
  content = getUrl(urln)  
  url2=re.compile('"primary":"(.+?)"', re.DOTALL).findall(content)[0]
  url2=url2.replace("\/","/")  
  Play(url2)
    
if mode == 'PlayVideo':
     playVideo(url)       
if mode == "":
    index()
if  mode =="Rubrik":
    Rubrik(url)    
if  mode =="Seite":
    Seite(url,offset)    
if  mode == "Play":
    Play(url)    
if  mode == "infofenster":
    infofenster(name,text,bild)        
if mode  == "playlive":
    playlive()