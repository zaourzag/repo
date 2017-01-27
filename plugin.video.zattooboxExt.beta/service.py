# coding=utf-8
#
#    ZattooBox Extended
#
#  Service on startup
#  (C)2017 by Steffen Rolapp
#


import xbmc, xbmcgui, xbmcaddon, datetime, time
import os, urlparse
from resources.library import library 
from resources.zattooDB import ZattooDB
_zattooDB_ = ZattooDB()          
__addon__ = xbmcaddon.Addon()
_listMode_ = __addon__.getSetting('channellist')
_library_=library()


              
def refreshProg():
    import urllib
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(300): break
        from resources.zattooDB import ZattooDB
        _zattooDB_ = ZattooDB()
        #update programInfo    
        startTime=datetime.datetime.now()
        endTime=datetime.datetime.now()+datetime.timedelta(minutes = 15)
        channels = _zattooDB_.getChannelList(_listMode_ == 'favourites')
        print 'StartRefresh  ' + str(datetime.datetime.now())
        _zattooDB_.getProgInfo(False, startTime, endTime)
        print "REFRESH Prog  " + str(datetime.datetime.now())

def recInfo():
    import urllib
    
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist', None)
    if resultData is None: return
    for record in resultData['recordings']:
        _zattooDB_.getShowInfo(record['program_id'])  
           
def start():
    import urllib
    try:
        _zattooDB_.updateChannels()
    except:
        _zattooDB_.updateChannels()
    _zattooDB_.updateProgram()
    
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    recInfo()
    _library_.make_library()   
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    
    channels = _zattooDB_.getChannelList(_listMode_ == 'favourites')
    Time=datetime.datetime.now()
    _zattooDB_.getProgInfo(True, Time, Time)

    xbmcgui.Dialog().notification('Programm Informationen', __addon__.getLocalizedString(30110),  __addon__.getAddonInfo('path') + '/icon.png', 5000, False) 

    refreshProg()  



if __addon__.getSetting('dbonstart') == 'true': start()
print "No DB--SERVICE"



