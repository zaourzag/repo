#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urlparse,urllib
import sqlite3
import time,datetime
import _strptime


__addon__ = xbmcaddon.Addon()


profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
translation = __addon__.getLocalizedString
  

base_url = sys.argv[0]
addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
translation = __addon__.getLocalizedString

  
try:
  if xbmcvfs.exists(temp):
    shutil.rmtree(temp)
  xbmcvfs.mkdirs(temp)
except:
  pass
       
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

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGDEBUG):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def insert(name,url,stunden,last):
    conn = sqlite3.connect(temp+'/cron.db')
    c = conn.cursor()    
    try:
        c.execute('insert into cron (name,url,stunden,last) values ("%s","%s",%d,%s)'%(name,url,stunden,last))
    except:
        var = traceback.format_exc()
        debug(var)
    conn.commit()
    c.close()    
def fixtime(date_string,format):
    debug("date_string,format :" +str(date_string)+","+str(format))
    try:
        x=datetime.datetime.strptime(date_string, format)
    except TypeError:
        x=datetime.datetime(*(time.strptime(date_string, format)[0:6]))
    return x

        
if __name__ == '__main__':
    notice("START")
    temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
    monitor = xbmc.Monitor()         
    while not monitor.abortRequested():  
      notice("LOOP")    
      try:
        conn = sqlite3.connect(temp+'/cron.db')      
        c = conn.cursor()          
        c.execute('select * from cron')    
        r = list(c)
        conn.commit()
        c.close()  
        for member in r:
            time=member[0]        
            url=member[1]
            #print("###### "+url)
            name=member[2]
            last=member[3]
            debug("###### "+last)
            now = datetime.datetime.now()
            date1 = fixtime(last, "%Y-%m-%d %H:%M:%S")
            if now>date1 + datetime.timedelta(hours=time):
                debug("ZEIT ABGELAUFEN "+last)
                conn = sqlite3.connect(temp+'/cron.db')      
                c = conn.cursor()    
                c.execute('update cron set last=datetime() where url="'+url+'"')
                conn.commit()           
                c.close()
            xbmc.executebuiltin('XBMC.RunPlugin('+url+')')           
      except:
         pass
      if monitor.waitForAbort(3600):                     
        break            
          