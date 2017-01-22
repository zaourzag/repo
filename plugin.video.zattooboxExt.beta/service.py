# coding=utf-8
#
#    ZattooBox Extended
#
#  Service on startup
#  (C)2017 by Steffen Rolapp
#


import xbmc, xbmcgui, xbmcaddon, datetime, time
import sys, urlparse
from resources.zattooDB import ZattooDB
from resources.library import library

_library_=library()
_zattooDB_ = ZattooDB()
__addon__ = xbmcaddon.Addon()
__addonId__=__addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
       
def refreshProg():
  while not xbmc.abortRequested:
    # update programInfo    
    startTime=datetime.datetime.now()+datetime.timedelta(minutes = 10)
    endTime=datetime.datetime.now()+datetime.timedelta(minutes = 10)
    _zattooDB_.getProgInfo(startTime, endTime)
    print "REFRESH Prog  " + str(datetime.datetime.now())
    xbmc.sleep(150000)
    
def start():
    _zattooDB_.reloadDB()
    _library_.make_library()
    
    Time=datetime.datetime.now()
    _zattooDB_.getProgInfo(Time, Time)
    xbmcgui.Dialog().notification('Programm Informationen', __addon__.getLocalizedString(30110),  __addon__.getAddonInfo('path') + '/icon.png', 000, False) 
       
    refreshProg()  
        
start()



