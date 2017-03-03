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
from HTMLParser import HTMLParser


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


def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
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

def addDir(name, url, mode, iconimage, desc="",text=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&text="+str(text)
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

def ListRubriken(urls,text,x=0):
 debug("ListRubriken url : "+urls)
 content2 = getUrl(urls)
 content = content2[content2.find('<section class="enw-block enw-block'):]
 content = content[:content.find('<div class="base-leaderboard">')]
 urlliste = content.split('<h3 class="enw-blockTopbar__title">') 
 anz=0
 urlold=[]
 for i in range(1, len(urlliste), 1):
   element=urlliste[i]   
   if "enw-btn__carouselNext" not in element:
      name = element[:element.find('</h3>')]
      name=artikeltext(name.strip())
      debug("++name : "+name )
      url=""
      if "<" in name:
          match = re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(name)
          if not "http:" in match[0][0]:
             url="http://"+language2+".euronews.com"+match[0][0]
          else:
             url=match[0][0]
          name=match[0][1]
      if "no_comment" in name:
          name="No Comment"
      name=cleanTitle(name)
      if url=="":
        url=name
      anz=url.count("/")     
      debug("------------" + str(anz))
      debug("------------" + url)
      if not "http://"+language2+".euronews.com/prog" in url and not url=="http://"+language2+".euronews.com/video" or anz>3 :
        if not url in urlold:
          urlold.append(url)
          debug(" ListRubrioken url: "+url)         
          debug(" ListRubrioken name: "+name)
          addDir(name, url, 'Rubrik', "", "",text=text) 
        anz=anz+1
 if anz>0:
   addDir("Artikel", urls, 'startvideos', "")
 if x>0:
        addDir("TimeLine", "", 'timeline', "")
 return anz    

 
 

def startvideos(url):
  debug("startvideos URL : "+url)
  content = getUrl(url)
  titlearray=[]
  urln=""
  #debug("Content :" + content)
  #content = content[content.find('<main id="enw-main-content" >'):]  
  #content = content[:content.find('div class="xlarge-3 enw-mpu1 show-for-xlarge">')]
  #debug("Content 2:" + content)
  Artikelliste = content.split('<article data-nid="') 
  anz=0
  for i in range(1, len(Artikelliste), 1):        
   try:
    element=Artikelliste[i]         
    debug("--------------------")
    debug(element)
    match = re.compile('<h[0-9] class="media__body__title">(.+?)</h[0-9]>', re.DOTALL).findall(element)
    title1=artikeltext(match[0])
    debug("Title1 :"+title1)
    if "<a rel" in title1:
      match = re.compile('>([^<]+?)<', re.DOTALL).findall(title1)
      debug("Title2 :"+match[0])
      title=artikeltext(match[0])
      match = re.compile('href="(.+?)"', re.DOTALL).findall(title1)
      if not "http" in match[0]:
        urln="http://"+language2+".euronews.com"+match[0]
      else:
        urln=match[0]
    match = re.compile('src="(.+?)"', re.DOTALL).findall(element)
    bild=match[0]
    if not "http" in bild:
       continue
    debug("bild :"+bild)
    if urln=="":
      match = re.compile('href="(.+?)"', re.DOTALL).findall(element)
      urln="http://"+language2+".euronews.com"+match[0]    
    debug("url :"+urln)
    if not title in titlearray:    
      titlearray.append(title)
      debug("Add link "+urln)
      addLink(title,urln, 'PlayVideo', bild, "")     
    anz=anz+1
   except:
     pass    
 
def playLive():    
    url="http://fr-par-iphone-1.cdn.hexaglobe.net/streaming/euronews_ewns/iphone_"+language+".m3u8"
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
     
def Aktuelle_meldungen(url,text):
  debug("Aktuelle_meldungen;" +url)
  content = getUrl("http://"+language2+".euronews.com")
  Artikelliste = content.split('<div class="scroll-horizontal ">') 
  count=0
  for i in range(1, len(Artikelliste), 1):
    element=Artikelliste[i]
    if url in element:
       element = element[:element.find('</div>')]
       match = re.compile('href="(.+?)">(.+?)</a>', re.DOTALL).findall(element)       
       for urlstring, text in match:
          if not "http:" in urlstring:
            url="http://"+language2+".euronews.com"+urlstring
          else:
            url =urlstring
          debug("Aktuelle_meldungen text:"+text)
          debug("Aktuelle_meldungen url:"+url)      
          addDir(text, url, 'Rubrik', "", "",text="0") 
          count=count+1
  
  
def Rubriknews(urls,text="0"):
   debug("Rubriknews urls :"+urls)
   if text=="-1":
      content = getUrl(urls)   
   else:
      content = getUrl(urls+"?offset="+text)   
   if "data-api-url" in content:
      match = re.compile('data-api-url="(.+?)"', re.DOTALL).findall(content)
      if not "http:" in match[0]:
        urls="http://"+language2+".euronews.com"+match[0]
      else:
        urls=match[0]
      content = getUrl(urls)
   struktur = json.loads(content)    
   anz=int(text)
   debug("starte ergebnis")
   debug("--------------------")
   debug(struktur)
   for element in struktur:
      debug("Nees Element")
      url=element["canonical"]
      title=element["title"]
      bild=element["images"][0]["url"]
      bild=bild.replace("{{w}}x{{h}}","608x342")
      debug ("---###---")
      debug (bild)
      debug ("---###---")
      addLink(title, url, 'PlayVideo', bild, "")  
      anz=anz+1
   if not text=="-1":
      addDir("Next", urls, 'Rubriknews', "", "",text=str(anz))           
def index():  
  ListRubriken("http://"+language2+".euronews.com","",x=1)
  addLink(translation(30001), "", 'playLive', "")
  addDir("Shows", "http://de.euronews.com/programme", 'Sendungen', "")
  addDir("Search", "", 'search', "")
  xbmcplugin.endOfDirectory(pluginhandle)   
  
def Sendungen():
  url="http://"+language2+".euronews.com"
  content = getUrl(url) 
  content = content[content.find('<li id="programs_link" data-accordion-item>'):]
  match = re.compile('<a href="(.+?)"', re.DOTALL).findall(content)
  newurl=url+match[0]
  content = getUrl(newurl)   
  buchstaben = content.split('<div class="letter-programs">')
  for i in range(1, len(buchstaben), 1):
         element=buchstaben[i]
         debug("Element :"+element)
         match = re.compile('href="(.+?)">', re.DOTALL).findall(element)  
         if not "http:" in match[0]:
            url="http://"+language2+".euronews.com"+match[0]
         else:
            url=match[0]
         match = re.compile('src="(.+?)"', re.DOTALL).findall(element)
         bild=match[0]
         match = re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(element)
         text=match[0]         
         if not "{{" in text:
           addDir(text, url, 'Rubrik', bild, "",text="0")   
  xbmcplugin.endOfDirectory(pluginhandle) 
  
  
  
  
def Rubrik(url,text):
  if "http" in url  :
     anz=ListRubriken(url,text)
     if anz==0:      
      try:
        Rubriknews(url) 
      except:        
        startvideos(url)      
  else:
      Aktuelle_meldungen(url,0)               
  xbmcplugin.endOfDirectory(pluginhandle)      
  
def playVideo(url):
    debug("Playvideo URL : " + url)
    fullUrl=""
    content = getUrl(url)
    match = re.compile('og:video" content="(.+?)"', re.DOTALL).findall(content)    
    if match:
        fullUrl = match[0] 
        debug("---- +"+ fullUrl)   
    else:
         try:
            match = re.compile('js-video-player" data-content="(.+?)"', re.DOTALL).findall(content)    
            jsonfile=match[0].replace("&quot;",'"')
            struktur = json.loads(jsonfile) 
            fullUrl=struktur["videos"][-1]["url"]
         except:
           pass
    if fullUrl!="":
      listitem = xbmcgui.ListItem(path=fullUrl)
      xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    else:
       listitem = xbmcgui.ListItem(path="")
       xbmcplugin.setResolvedUrl(pluginhandle, False, listitem)
       match = re.compile('<meta name="date.updated" content="([^"]+)"', re.DOTALL).findall(content)
       datum=match[0]                           
       match = re.compile('<meta property="og:title" content="(.+?)"/>', re.DOTALL).findall(content)
       title_artikel=match[0]
       title_artikel=datum + " "+ title_artikel
       match = re.compile('og:image" content="(.+?)"', re.DOTALL).findall(content)
       if match:
         text = content[content.find('<div class="article__content" itemprop="articleBody">'):]
         text=text.replace('<div class="article__content" itemprop="articleBody">','')
         text = text[:text.find('<blockquote class="twitter-tweet"')]
         text = text[:text.find('</div>')]
         text=artikeltext(text)
         bild=match[0]
         if text=="":
           nurbild=1
         else:
           nurbild=0         
       else:
            fototext = content[content.find('<div id="potd-wrap" class="col-m-b clear">'):]
            fototext = fototext[:fototext.find('</div>')]
            text = fototext[fototext.find('<div id="image-caption">'):]
            text=artikeltext(text)
            match = re.compile('<img src="(.+?)"', re.DOTALL).findall(fototext)
            bild=match[0]
            debug("playVideo : 1")
            nurbild=1
       debug("BILD :"+bild)
       debug("nurbild :"+str(nurbild))
       window = Infowindow(title=title_artikel,text=text,image=bild,nurbild=nurbild)
       window.doModal()
       del window

def search():    
     dialog = xbmcgui.Dialog()
     d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
     d=urllib.quote(d, safe='')
     url="http://"+language2+".euronews.com/api/search?query="+ d 
     Rubriknews(url,text="-1")
     xbmcplugin.endOfDirectory(pluginhandle)
def timeline(stamp):
     debug("TIMELINE URL: ")
     urln="http://"+language2+".euronews.com/api/timeline.json?limit=20"
     if stamp!="":
        urln=urln+"&after="+stamp     
     content = getUrl(urln)     
     jsonurl=artikeltext(content)
     struktur = json.loads(jsonurl)
     for element in struktur:
        datum=element['createdAt']
        zeitstring=time.strftime("%H:%M", time.localtime(datum))
        urltime=time.strftime("/%Y/%m/%d", time.localtime(datum))
        title=element['title']
        url="http://"+language2+".euronews.com"+urltime+element['url']
        debug("URL" + url)
        bild=element["images"][0]["url"]
        bild=bild.replace("{{w}}x{{h}}","608x342")
        addLink(zeitstring+ " "+title, url, 'PlayVideo', bild, "")
     addDir("Next", str(datum), 'timeline', "", "")     
     xbmcplugin.endOfDirectory(pluginhandle)
     debug("timeline : "+jsonurl)
     
if mode == 'listVideos':
   listVideos()
elif mode == 'playLive':
    playLive()
elif mode == 'Rubrik':
    Rubrik(url,text)    
elif mode == 'startvideos':
    startvideos(url)          
    xbmcplugin.endOfDirectory(pluginhandle) 
elif mode == 'Rubriknews':
    Rubriknews(url,text)      
elif mode == 'PlayVideo':
     playVideo(url)       
elif mode == 'search':
     search()    
elif mode == 'timeline':
     timeline(url)  
elif mode == 'Sendungen':
     Sendungen()           
else:
    index()
