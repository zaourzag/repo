# coding=utf-8
#
#    ZattooBox Extended
#
#  Service on startup
#  (C)2017 by Steffen Rolapp
#


import xbmc, xbmcgui, xbmcaddon, datetime, time
import sys, urlparse

from resources.library import library
from resources.zattooDB import ZattooDB

_zattooDB_ = ZattooDB()
_library_=library()
__addon__ = xbmcaddon.Addon()
__addonId__=__addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')

              
def refreshProg(self):
    import urllib
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(60): break
        #update programInfo    
        startTime=datetime.datetime.now()+datetime.timedelta(minutes = 5)
        endTime=datetime.datetime.now()+datetime.timedelta(minutes = 5)

        _zattooDB_.getProgInfo(False, startTime, endTime)
        print "REFRESH Prog  " + str(datetime.datetime.now())
        
           
def start():
    import urllib
    _zattooDB_.updateChannels()
    _zattooDB_.updateProgram()
    
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    _library_.make_library()   
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    
    Time=datetime.datetime.now()
    _zattooDB_.getProgInfo(True, Time, Time)

    xbmcgui.Dialog().notification('Programm Informationen', __addon__.getLocalizedString(30110),  __addon__.getAddonInfo('path') + '/icon.png', 5000, False) 

    #refreshProg()  



if __addon__.getSetting('dbonstart') == 'true': start()

print "No DB--SERVICE"



