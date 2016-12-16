#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcvfs
import json,cookielib,urllib2,re,urlparse,os
import pyxbmct
from difflib import SequenceMatcher

addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       
cookie=temp+"/cookie.jar"
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

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
  
def geturl(url,data="x",header=""):
        global cj
        print("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
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
             #print e.code   
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        return content


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
    
class Infowindow(pyxbmct.AddonDialogWindow):
    text=""
    pos=0
    def __init__(self, title='',text='',image=""):
        super(Infowindow, self).__init__(title)
        self.setGeometry(600,600,8,8)        
        self.bild=image
        self.text=text        
        self.set_info_controls()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_info_controls(self):
      self.textbox=pyxbmct.TextBox()            
      self.placeControl(self.textbox, 2, 0, columnspan=8,rowspan=6)                       
      self.textbox.setText(self.text)
      self.image = pyxbmct.Image(self.bild)
      self.placeControl(self.image, 0, 0,columnspan=8,rowspan=2)
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
              
              
if __name__ == '__main__':
    addon = xbmcaddon.Addon()
    
    info = sys.listitem.getVideoInfoTag()
    title=info.getTVShowTitle()
    if title=="":
     title=sys.listitem.getLabel()
    debug("TITLE :::: "+title)
    
    suchtitle=title.replace(" ","+")
    try:
      suchtitle2 = re.compile('(.+?)\+\([0-9]+\)', re.DOTALL).findall(suchtitle)[0]     
      suchtitle=suchtitle2
    except:
      pass
    xc=geturl("http://www.serienjunkies.de/suchen.php")
    url="http://www.serienjunkies.de/suchen.php?s="+suchtitle+"+XXXX&a=s&t=0"
    debug("URL :"+url)
    content=geturl(url)
    match = re.compile('<div class="sminibox"><a href="(.+?)"><img src="(.+?)"[^"]+?alt="(.+?)"/>', re.DOTALL).findall(content)
    maxlink=""
    maxnr=0
    for link,image,name in match:
      name_comp=name.replace(" ","")
      try:
        name_comp1 = re.compile('(.+?)\([0-9]+\)', re.DOTALL).findall(name_comp)[0]  
        name_comp=name_comp1
      except:
         pass
      title_comp=title.replace(" ","")
      try:
        title_comp1 = re.compile('(.+?)\([0-9]+\)', re.DOTALL).findall(title_comp)[0]  
        title_comp=title_comp1
      except:
         pass
      xy=similar(title_comp,name_comp)
      if xy>0.8:    
          if xy>maxnr:
            maxnr=xy 
            maxlink=link
          debug("Treffer")
      else:
           debug("Kein Treffer")
      debug("name_comp :"+name_comp)
      debug("title_comp : "+title_comp)      
      debug("#############" + str(xy))
    debug("maxlink : "+maxlink)
    if maxlink=="":
        xbmc.executebuiltin('Notification('+title+',"Serie nicht gefunden")')
    else:
        newlink="http://www.serienjunkies.de"+maxlink+"alle-serien-staffeln.html"
        content=geturl(newlink)            
        Bild = re.compile('property="og:image" content="(.+?)"', re.DOTALL).findall(content)[0]   
        Zusammenfassung = re.compile('<p class="box clear pad5">(.+?)</p>', re.DOTALL).findall(content)[0]   
        Zusammenfassung=Zusammenfassung.replace("</a>","")   
        wegs = re.compile('(<.+?>)', re.DOTALL).findall(Zusammenfassung)
        for weg in wegs:
            Zusammenfassung=Zusammenfassung.replace(weg,"")     
        debug("Zusammenfassung : "+Zusammenfassung)
        debug("---")
        Zusammenfassung=Zusammenfassung.replace("&uuml;","ü")
        Zusammenfassung=Zusammenfassung.replace("&auml;","ä")
        Zusammenfassung=Zusammenfassung.replace("&ouml;","ö")
        Zusammenfassung=Zusammenfassung.replace("&szlig;","ß")    
        window = Infowindow(title="SerienFino",text=Zusammenfassung,image=Bild)
        window.doModal()
        del window
    cj.save(cookie,ignore_discard=True, ignore_expires=True)