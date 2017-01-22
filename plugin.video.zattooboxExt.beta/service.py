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
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(300): break
        # update programInfo    
        startTime=datetime.datetime.now()+datetime.timedelta(minutes = 5)
        endTime=datetime.datetime.now()+datetime.timedelta(minutes = 5)
        _zattooDB_.getProgInfo(False, startTime, endTime)
        print "REFRESH Prog  " + str(datetime.datetime.now())


def recInfo():
    import urllib
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist', None)
    if resultData is None: return
    for record in resultData['recordings']:
        showInfo=_zattooDB_.getShowInfo(record['program_id']) 
           
def start():
    _zattooDB_.updateChannels()
    _zattooDB_.updateProgram()
    
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    recInfo()
    _library_.make_library()   
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    
    Time=datetime.datetime.now()
    _zattooDB_.getProgInfo(True, Time, Time)

    xbmcgui.Dialog().notification('Programm Informationen', __addon__.getLocalizedString(30110),  __addon__.getAddonInfo('path') + '/icon.png', 5000, False) 

    refreshProg()  



if __addon__.getSetting('dbonstart') == 'true': start()

print "No DB--SERVICE"



