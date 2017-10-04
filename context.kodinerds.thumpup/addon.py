#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcvfs
import json,urllib2,re,urlparse,os
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from datetime import datetime    
import urllib
import requests,cookielib
from cookielib import LWPCookieJar
cj = cookielib.CookieJar()
addon = xbmcaddon.Addon()
from thetvdb import TheTvDb

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
session = requests.session()

if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

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
  
  
def geturl(url,data="x",header=[]):
   global cj
   content=""
   debug("URL :::::: "+url)
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   userAgent = "Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1"
   header.append(('User-Agent', userAgent))
   header.append(('Accept', "*/*"))
   header.append(('Content-Type', "application/json;charset=UTF-8"))
   header.append(('Accept-Encoding', "plain"))   
   opener.addheaders = header
   try:
      if data!="x" :
         request=urllib2.Request(url)
         cj.add_cookie_header(request)
         content=opener.open(request,data=data).read()
      else:
         content=opener.open(url).read()
   except urllib2.HTTPError as e:
       debug ( e)
   opener.close()
   return content



def gettitle()  :
  title=""
  title=xbmc.getInfoLabel('ListItem.TVShowTitle')
  try:    
    info = sys.listitem.getVideoInfoTag() 
    title=info.getTVShowTitle()
  except:
    pass
  try:
      title=xbmc.getInfoLabel('ListItem.TVShowTitle')
  except:
       pass
  if title=="":
     title = xbmc.getInfoLabel("ListItem.Title").decode('UTF-8')      
  if title=="":
     title=sys.listitem.getLabel()
  debug("TITLE :::: "+title)     
  return title

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

addon = xbmcaddon.Addon()    
debug("Hole Parameter")
debug("Argv")
debug(sys.argv)
debug("----")
try:
      params = parameters_string_to_dict(sys.argv[2])
      debug("Parameter Holen geklappt")
except:
      debug("Parameter Holen nicht geklappt")
      mode="" 
debug("Mode ist : "+mode)
if mode=="":  
    username=addon.getSetting("username")
    password=addon.getSetting("password")
    if username=="" or password=="":
      dialog = xbmcgui.Dialog()
      ok = dialog.ok('Username oder Password fehlt', 'Username oder Password fehlt')
      exit    
    title=gettitle()
    tvdb = TheTvDb()
    wert=tvdb.search_series(title,prefer_localized=True)
    debug(wert)
    count=0
    gefunden=0
    wertnr=0
    for serie in wert:
      serienname=serie["seriesName"]
      nummer=similar(title,serienname)
      if nummer >wertnr:
        wertnr=nummer
        gefunden=count
      count+=1
    if count>0:      
      idd=wert[gefunden]["id"]
      seriesName=wert[gefunden]["seriesName"]
      serienstart=wert[gefunden]["firstAired"]
      inhalt=wert[gefunden]["overview"]
      serie=tvdb.get_series(idd)
      Bild=serie["art"]["banner"]
      summ=tvdb.get_series_episodes_summary(idd)
      anzahLstaffeln = int(sorted(summ["airedSeasons"],key=int)[-1])    
      dialog=xbmcgui.Dialog()
      ret=dialog.yesno("Serienname richtig?", "Ist der Serienname "+seriesName +" richtig?")
      if ret==False:
         count=0         
         seriesName=title
      debug("Gefunden :"+seriesName)
    ret=dialog.yesno("Serie Emfehlen?", "Serienname "+seriesName +" emfehlen?")           
    if ret==False:
       exit
    if title=="":
       dialog = xbmcgui.Dialog()
       ok = dialog.ok('Fehler', 'Selectiertes File Hat kein Serie Hinterlegt')
       exit
    content=geturl("https://www.kodinerds.net/")    
    newurl=re.compile('method="post" action="(.+?)"', re.DOTALL).findall(content)[0]
    sec_token=re.compile("SECURITY_TOKEN = '(.+?)'", re.DOTALL).findall(content)[0]
    content=geturl("https://www.kodinerds.net/index.php/Login/",data="username="+username+"&action=login&password="+password+"&useCookies=1&submitButton=Anmelden&url="+newurl+"&t="+sec_token)
    if "Angaben sind ung" in content or "Anmelden oder registrieren"in content:
      dialog = xbmcgui.Dialog()
      ok = dialog.ok('Username oder Password ungueltig', 'Username oder Password ungueltig')
      exit    
    content=geturl("https://www.kodinerds.net/index.php/Thread/58034-L0RE-s-Test-thread/")

    sec_token=re.compile("SECURITY_TOKEN = '(.+?)'", re.DOTALL).findall(content)[0]
    hash=re.compile('name="tmpHash" value="(.+?)"', re.DOTALL).findall(content)[0]
    timestamp=re.compile('data-timestamp="(.+?)"', re.DOTALL).findall(content)[0]
    text="[url='https://www.kodinerds.net/index.php/Thread/58030-Doofe-ideen/\']Aus Kodi Emfolen :[/url] '"+ seriesName+'"'    
    if count>0:    
      text=text+"\n"+"[img]"+Bild+"[/img]\n"
      text=text+"Gestartet am : "+serienstart+"\n"
      text=text+"Anazhl Staffeln :"+str(anzahLstaffeln)+"\n"
      text=text+inhalt+"\n"      
      try:
        movidedb="https://api.themoviedb.org/3/find/"+str(idd)+"?api_key=f5bfabe7771bad8072173f7d54f52c35&language=en-US&external_source=tvdb_id"
        content=geturl(movidedb)
        serie = json.loads(content)
        debug("Moviedb")
        debug(serie)
        sid=serie["tv_results"][0]["id"]      
        movidedb="https://api.themoviedb.org/3/tv/"+str(sid)+"/videos?api_key=f5bfabe7771bad8072173f7d54f52c35&language=en-US"
        content=geturl(movidedb)
        trailers = json.loads(content)        
        debug(trailers)
        zeige=""
        nr=0
        for trailer in trailers["results"]:
          wertung=0
          key=trailer["key"]
          debug("KEY :"+key)
          site=trailer["site"]
          type=trailer["type"]
          if site=="YouTube":
            if "railer" in type:
                wertung=2
            else:
                wertung=1
          if wertung>nr:
            zeige=key
            nr=wertung
        if not zeige=="":
           debug("FOUND :"+zeige)
           text=text+"[url='https://www.youtube.com/watch?v="+zeige+"']Trailer[/url]"      
      except:
        pass
    text=text.encode("utf-8")
    values = {
      'actionName' : 'quickReply',
      'className' : 'wbb\data\post\PostAction',
      'interfaceName': 'wcf\data\IMessageQuickReplyAction',
      'parameters[objectID]': '58034',
      'parameters[data][message]' : text,
      'parameters[data][tmpHash]' : hash,
      'parameters[lastPostTime]':timestamp,
      'parameters[pageNo]':'1'
    }
    data = urllib.urlencode(values)
    content=geturl("https://www.kodinerds.net/index.php/AJAXProxy/?t="+sec_token,data=data)
    if content == ""  : 
      dialog = xbmcgui.Dialog()
      ok = dialog.ok('Posten hat nicht Geklappt', 'Posten hat nicht Geklappt. Posten nur alle 30 Sek möglich')
      exit    
    debug(content)
    
    

    
