#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse,json
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib,json
import shutil
import re,md5
import socket, cookielib
import feedparser
import HTMLParser,xbmcplugin
from dateutil import parser
from django.utils.encoding import smart_str

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('path') )
background = os.path.join(__addondir__,"bg.png")

profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
translation = __addon__.getLocalizedString

popupaddon=xbmcaddon.Addon("service.popwindow")
popupprofile    = xbmc.translatePath( popupaddon.getAddonInfo('profile') ).decode("utf-8")
popuptemp       = xbmc.translatePath( os.path.join( popupprofile, 'temp', '') ).decode("utf-8")
  
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
defaultBackground = ""
defaultThumb = ""


def geturl(url):
   debug("geturl url : "+url)
   cj = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt
   
def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
    
# Einlesen von Parametern, Notwendig für Reset der Twitter API
def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict

if not xbmcvfs.exists(temp):
   xbmcvfs.mkdirs(temp)



def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})  
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
        iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
    liz.setProperty('IsPlayable', 'true')
    liz.addStreamInfo('video', { 'duration' : duration })
    liz.setProperty("fanart_image", iconimage)
    #liz.setProperty("fanart_image", defaultBackground)
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok
    
        
def savemessage(message,image,grey,lesezeit)  :    
    message = smart_str(message)
    image=unicode(image).encode('utf-8')
    debug("message :"+message)
    debug("image :"+image)
    debug("grey :"+grey)
    debug("popuptemp :"+popuptemp)
    debug("lesezeit :"+str(lesezeit))
    filename=md5.new(message).hexdigest()  
    f = open(popuptemp+"/"+filename, 'w')    
    f.write(message+"###"+image+"###"+grey+"###"+str(lesezeit))
    f.close()   
    

def ersetze(text):
# 
    text=text.replace("<br>","").replace("<b>","").replace("</b>","").replace("<br/>","")
    text=text.replace ("</p>","").replace("<p>","").replace("<div id='articleTranscript'>","").replace("<br />","").replace('<div id="image-caption">',"").replace("  ","").replace("<p","")
    text=text.replace ("<em>","").replace("</em>","")
    text=text.replace ("<h3>","").replace("</h3>","")
    text=text.replace ('<span class="rottext>',"")
    text=text.replace ('<span class="gruentext>',"")
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
    text = text.replace('\/', "/")    
    #text = text.replace('\n', "")    
    text = text.strip()
    return text
  
    
def delspiel(id,liste):
  fileinhalt=""
  filename       = xbmc.translatePath( os.path.join( temp, 'spiel.txt') ).decode("utf-8")
  for zeile in liste:
    if not str(id) in zeile and "##" in zeile:
         fileinhalt=fileinhalt+"\n"+zeile          
  fp = open(filename, 'w')    
  fp.write(fileinhalt)
  fp.close()    

   
if __name__ == '__main__':
    cimg=""
    xbmc.log("FussballPupup:  Starte Plugin")

    schown=[]
    monitor = xbmc.Monitor()   
    
    while not monitor.abortRequested():
      titlelist=[]
      cimglist=[]
      greyoutlist=[]
      lesezeitlist=[]
      timelist=[] 
      ids=[]
      ins=[]
      auss=[]
      anzal_meldungen=[]      
      xbmc.log("Hole Umgebung")
      bild=__addon__.getSetting("bild") 
      lesezeit=__addon__.getSetting("lesezeit")
      greyout=__addon__.getSetting("greyout")
      filename       = xbmc.translatePath( os.path.join( temp, 'spiel.txt') ).decode("utf-8")
      gesamtliste=[]
      if xbmcvfs.exists(filename) :
        fp=open(filename,"r") 
        contentf=fp.read()
        fp.close()          
        liste=contentf.split("\n")                
        for spiel in liste:  
          in_spieler=""
          out_spieler=""
          if  "##" in spiel:          
            arr=spiel.split("##")
            name=arr[0]
            live_status=arr[1]
            lieganr=arr[2]
            dayid=arr[3]     
            spielnr=arr[4]            
            aus=arr[5]
            inn=arr[6]
            match_date=arr[7]
            match_time=arr[8]  
            zeitpunkt=match_date+ " "+match_time
            dt = parser.parse(zeitpunkt)  
            lss=dt.timetuple()
            lsv=time.mktime(lss)                       
            
            nurl="https://api.sport1.de/api/sports/matches-by-season/co"+lieganr+"/se/md"+dayid
            content=geturl(nurl) 
            struktur = json.loads(content)
            tage=struktur["round"]
            breakit=0
            for tag in tage:
              spiele=tag["match"]
              for spiel in spiele:
                id=spiel["id"] 
                ende=spiel["finished"]             
                if str(id)==spielnr: 
                  if not ende=="no":
                     delspiel(id,liste)
                     breakit=1
            if breakit==1:
              continue
            #if live_status=="full":
            #   url="https://api.sport1.de/api/sports/liveticker/co"+lieganr+"/ma"+spielnr
            #   content=geturl(url)
            #   struktur = json.loads(content)
            #   for element in struktur:
            #       debug("######")
            #       debug(element)
            #       zeit=element["tickertime"]
            #       minute=element["minute"]
            #       dt = parser.parse(zeit)  
            #       news=ersetze(element["content"])
            #       id=element["id"]
            #       text=str(minute) +" Minute "+inn +" & "+aus+" # "+ news
            #       titlelist.append(text)
            #       cimglist.append("")
            #       greyoutlist.append(greyout)
            #       lesezeitlist.append(lesezeit) 
            #       ins.append(inn)
            #       auss.append(aus)
            #       timelist.append(time.mktime(dt.timetuple())) 
            #       ids.append(id)
            #   #Spieler MÜLLER von Maschaft BAYERN schiesst in der X Minute ein Tor [ + Spielstand 3:0 ] 
            #else:
            url="https://api.sport1.de/api/sports/match-event/ma"+spielnr
            content=geturl(url)
            struktur = json.loads(content)
            ccontent="0:0"
            anzal_meldung=0
            for element in struktur:
                 anzal_meldung=anzal_meldung+1
                 minute=element["minute"]
                 action=element["action"]
                 kind=element["kind"]
                 if not element["content"]=="":
                    ccontent=smart_str(element["content"])
                 #team=element["team"]["shortname"]
                 #person=element["person"]["name"]
                 #personid=element["person"]["id"]
                 created=element["created"]
                 id=element["id"]                 
                 Meldung=""
                 if action=="match":
                    if kind=="game-end":
                      Meldung=" Das Spiel "+ inn +" gegen "+aus +" Endete mit "+ccontent
                    if kind=="game-start":
                      Meldung=" Das Spiel "+ inn +" gegen "+aus +" hat Begonnen"
                    if kind=="first-half-end":
                      Meldung="Die Erste Halbzeit des Spiels "+ inn +" gegen "+aus +" ist zuende. Es steht "+ccontent                  
                    if kind=="second-half-start":
                      Meldung="Die Zweite Halbzeit des Spiels "+ inn +" gegen "+aus +" hat begonnen. Es steht "+ccontent            
                    if kind=="second-half-end":
                      Meldung="Die Zweite Halbzeit des Spiels "+ inn +" gegen "+aus +" ist zuende. Es steht "+ccontent                          
                    if kind=="first-extra-start":
                      Meldung="Die Erste Hälfte der Verlaengerung des Spiels "+ inn +" gegen "+aus +" hat Begonnen. Es steht "+ccontent          
                    if kind=="first-extra-end":
                      Meldung="Die Erste Hälfte der Verlaengerung des Spiels "+ inn +" gegen "+aus +" ist zuende. Es steht "+ccontent                           
                    if kind=="second-extra-start":
                      Meldung="Die Zweite Hälfte der Verlaengerung des Spiels "+ inn +" gegen "+aus +" hat begonnen. Es steht "+ccontent                                                 
                    if kind=="second-extra-end":
                      Meldung="Die Zweite Hälfte der Verlaengerung des Spiels "+ inn +" gegen "+aus +" ist zuende. Es steht "+ccontent                                                 
                    if kind=="penalty-start":
                      Meldung="Das Elfmeter Schiesse des Spiels "+ inn +" gegen "+aus +" hat begonnen. Es steht "+ccontent                                                 
                 if action=="card":
                    team=element["team"]["name"]
                    person=element["person"]["name"]
                    personid=element["person"]["id"]
                    if kind=="yellow":
                        Meldung=minute +" Minute: Gelbe Karte fuer "+ person +" von "+ team 
                    if kind=="red":
                        Meldung=minute +" Minute: Rote Karte fuer "+ person +" von "+ team 
                 if action=="goal": 
                    team=element["team"]["name"]
                    person=element["person"]["name"]
                    personid=element["person"]["id"]
                    if kind=="penalty":    
                       Meldung=minute +" Minute: Tor durch Strafstoss von "+ person +" von "+ team +". Es steht "+ccontent                    
                    if kind=="goal": 
                       Meldung=minute +" Minute: Tor durch"+ person +" von "+ team +  "Es steht "+ccontent                                     
                 if action=="pso":  
                    team=element["team"]["name"]
                    person=element["person"]["name"]
                    personid=element["person"]["id"]                 
                    if kind=="goal": 
                       Meldung="Elf Meter Schiessen Tor von "+ person +" für "+ team
                    if kind=="goal": 
                       Meldung="Elf Meter Schiessen Verfehl von "+ person +" für "+ team
                 if action=="playing":
                    team=element["team"]["name"]
                    person=element["person"]["name"]
                    personid=element["person"]["id"] 
                    if kind=="substitute-out":                        
                        out_spieler=person
                        Meldung=""
                    if kind=="substitute-in":                               
                        in_spieler=person
                        Meldung=""
                    if not in_spieler=="" and not out_spieler=="":
                        Meldung=minute +" Minute: "+team +" tauscht "+out_spieler +" durch "+in_spieler 
                        in_spieler=""
                        out_spieler=""
                 if action=="goal":  
                    team=element["team"]["name"]
                    person=element["person"]["name"]
                    personid=element["person"]["id"]  
                    Meldung=minute +" Minute: Spieler "+person +" schiesst ein Tor fuer "+team+". Es steht nun : "+ ccontent
                 if not Meldung=="":
                  titlelist.append(Meldung)
                  cimglist.append("")
                  greyoutlist.append(greyout)
                  lesezeitlist.append(lesezeit) 
                  ins.append(inn)
                  auss.append(aus)    
                  anzal_meldungen.append(anzal_meldung)
                  debug("-------------> TIME NEU :"+str(lsv+int(minute*60)))
                  timelist.append(lsv+int(minute*60))                    
                  ids.append(id)
        if len(timelist)>0 :
          timelist,anzal_meldungen,titlelist,cimglist,lesezeitlist,greyoutlist,ids,ins,auss = (list(x) for x in zip(*sorted(zip(timelist,anzal_meldungen,titlelist,cimglist,lesezeitlist,greyoutlist,ids,ins,auss))))            
          for i in range(len(titlelist)):     
            if not ids[i] in  schown:
                debug("Zeit ist : "+str(timelist[i]))
                savemessage(titlelist[i],cimglist[i],greyoutlist[i],lesezeitlist[i])             
                schown.append(ids[i])                   
      if monitor.waitForAbort(60):
        break            
      
           
      
