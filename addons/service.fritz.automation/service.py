#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib, zlib,json
import shutil
import re
from xml.dom.minidom import parseString
import md5
import hashlib
import cookielib

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('path') )
cj = cookielib.CookieJar()

# inhalt=__addon__.getSetting("inhalt")
profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

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
        

def getUrl(url,data="X"):
        print("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
        opener.addheaders = [('User-Agent', userAgent)]
        content=""
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             print e
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
  
def getSessionID(baseuri, username, password, sid = None):
  if sid == None:
    uri = baseuri + "/login_sid.lua"
  else:
    uri = baseuri + "/login_sid.lua?sid="+sid

  req = urllib2.urlopen(uri)
  data = req.read()
  #print "data from checking sid:"
  #print data

  xml = parseString(data)
  sid = xml.getElementsByTagName("SID").item(0).firstChild.data

  #print "sid",sid
  if sid != "0000000000000000":
    return sid
  else:
    challenge = xml.getElementsByTagName("Challenge").item(0).firstChild.data
    #print "challenge",challenge
    uri = baseuri + "/login_sid.lua"
    post_data = urllib.urlencode({'username' : username, 'response' : createResponse(challenge,password), 'page' : ''})
    #print "req uri:",uri, post_data
    req = urllib2.urlopen(uri, post_data)
    data = req.read()
    #print "data from login:"
    #print req.info()
    #print data
    xml = parseString(data)
    sid = xml.getElementsByTagName("SID").item(0).firstChild.data
    #print "sid",sid
    if sid == "0000000000000000": raise FritzError("login to fritzbox failed")
    return sid

def createResponse(challenge, password):
  text = "%s-%s" % (challenge, password)
  text = text.encode("utf-16le")
  res = "%s-%s" % (challenge, hashlib.md5(text).hexdigest())
  #print "md5: [%s]" % res
  return res
def readids():
     deviceids=[]
     deviceids.append("")
     devicenames=[]
     devicenames.append("Keine Aktion")
     allstrings=[]
     allstrings.append("Keine Aktion")
     atkion=""
     aktion_id=""
     global ip 
     global password
     if ip and password:
       Menu1=[]
       Menu1.append("TV is Running")
       Menu1.append("TV is not Running")
       Menu1.append("Video is Running")
       Menu1.append("Video is not Running")
       dialog = xbmcgui.Dialog()
       nr=dialog.select("Select Action", Menu1)
       if nr>=0:
         if nr==0 :
            aktion="tvon"
            aktionid="idtvon"
         if nr==1 :
            aktion="tvoff"
            aktionid="idtvoff"
         if nr==2 :
            aktion="videoon"
            aktionid="idvideoon"
         if nr==3 :
            aktion="videooff"
            aktionid="idvideooff"
         baseurl="http://"+ip             
         sid=getSessionID(baseurl,"",password)
         debug("SID : "+sid)
         url=baseurl +"/webservices/homeautoswitch.lua?switchcmd=getdevicelistinfos&sid="+sid
         content=getUrl(url)
         xml = parseString(content)
         devices = xml.getElementsByTagName("device")
         for device in devices:
          namexml=device.getElementsByTagName("name")[0]
          name=namexml.firstChild.data
          devid=device.getAttribute('identifier')
          devicenames.append(name)
          deviceids.append(devid)
          allstrings.append(name + "( "+ devid +" )")        
         dialog = xbmcgui.Dialog()
         nr=dialog.select("Menu", allstrings)
         if nr>=1:
             name=devicenames[nr]
             ids=deviceids[nr]           
             Menu3=[]
             Menu3.append("Einschalten")
             Menu3.append("Auschalten")
             dialog = xbmcgui.Dialog()
             nr=dialog.select("Select Strom", Menu3)
             if nr >=0:
                if nr==0 :
                  zustand="Ein"
                if nr==1 :
                  zustand="Aus"
                __addon__.setSetting(id=aktion, value=zustand)                
                __addon__.setSetting(id=aktionid, value=ids)                                
         else:
                __addon__.setSetting(id=aktion, value="")                
                __addon__.setSetting(id=aktionid, value="")         
if len(sys.argv) > 1:
    params = parameters_string_to_dict(sys.argv[2])
    mode = urllib.unquote_plus(params.get('mode', ''))
    if mode=="clear":      
      xbmc.log("Starte Settings")                              
      ip=__addon__.getSetting("ip")  
      username=__addon__.getSetting("username")  
      password=__addon__.getSetting("password")  
      tvon=__addon__.getSetting("tvon")        
      tvon_id=__addon__.getSetting("idtvon")         
      tvoff=__addon__.getSetting("tvoff")   
      tvoff_id=__addon__.getSetting("idtvoff")
      videoon=__addon__.getSetting("videoon")        
      videoon_id=__addon__.getSetting("idvideovon")         
      videooff=__addon__.getSetting("videooff")   
      videooff_id=__addon__.getSetting("idvideooff")               
      readids()
       
#      dialog2 = xbmcgui.Dialog()      
 #     ok = xbmcgui.Dialog().ok( "Neu Configuration", "Nach verlassen des Einstellungen wird Twitter neu Configuriert" )   
 #     exit()            


if __name__ == '__main__':
    xbmc.log("Twitter:  Starte Plugin")
    oldip=""
    oldusername=""
    oldpassword=""    
    oldurl=""
    # Starte Service
    monitor = xbmc.Monitor()    
    # Solange der Service läuft
    while not monitor.abortRequested():  
    
      ip=__addon__.getSetting("ip")  
      username=__addon__.getSetting("username")  
      password=__addon__.getSetting("password") 
      baseurl="http://"+ip       
      if oldpassword!=password or oldusername!=username or oldip!=ip:
         debug("Es hat sich was geändert")
         if password!="" and ip!="" :
           debug ("Authentifiziere")           
           sid=getSessionID(baseurl,username,password)                      
         oldpassword=password
         oldusername=username
         oldip=ip            
      if monitor.waitForAbort(5):
        break            
      tvon=__addon__.getSetting("tvon")        
      tvon_id=__addon__.getSetting("idtvon")         
      tvoff=__addon__.getSetting("tvoff")   
      tvoff_id=__addon__.getSetting("idtvoff") 
      videoon=__addon__.getSetting("videoon")        
      videoon_id=__addon__.getSetting("idvideoon")         
      videooff=__addon__.getSetting("videooff")   
      videooff_id=__addon__.getSetting("idvideooff")          
      # Nur wenn ein Fernsehnder an ist      
      if xbmc.getCondVisibility('Pvr.IsPlayingTv'):             
             status=tvon 
             thisid=tvon_id
             if tvon=="Ein":
               url=baseurl +"/webservices/homeautoswitch.lua?ain="+tvon_id+"&switchcmd=setswitchon&sid="+sid               
             else:
               url=baseurl +"/webservices/homeautoswitch.lua?ain=" +tvon_id +"&switchcmd=setswitchoff&sid="+sid
             xbmc.log("TV Läuft")
      elif not xbmc.Player().isPlaying() :
             status=tvoff
             thisid=tvoff_id
             if tvoff=="Ein":
              url=baseurl +"/webservices/homeautoswitch.lua?ain="+tvoff_id+"&switchcmd=setswitchon&sid="+sid
             else:
              url=baseurl +"/webservices/homeautoswitch.lua?ain="+tvoff_id+"&switchcmd=setswitchoff&sid="+sid   
         
      if xbmc.Player().isPlaying() and not xbmc.getCondVisibility('Pvr.IsPlayingTv'):             
          if videoon=="Ein":
             url=baseurl +"/webservices/homeautoswitch.lua?ain="+videoon_id+"&switchcmd=setswitchon&sid="+sid               
          else:
             url=baseurl +"/webservices/homeautoswitch.lua?ain=" +videoon_id +"&switchcmd=setswitchoff&sid="+sid
             xbmc.log("TV Läuft")
      elif not xbmc.getCondVisibility('Pvr.IsPlayingTv'):
          if videooff=="Ein":
               url=baseurl +"/webservices/homeautoswitch.lua?ain="+videooff_id+"&switchcmd=setswitchon&sid="+sid
          else:
               url=baseurl +"/webservices/homeautoswitch.lua?ain="+videooff_id+"&switchcmd=setswitchoff&sid="+sid                    
               
      if not oldurl==url:
         content=getUrl(url)             
         oldurl=url
         debug("Schalte Um URL:" + url)
             
     
      
      