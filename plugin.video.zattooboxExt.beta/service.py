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
_library_=library()
localString = __addon__.getLocalizedString

              
def refreshProg():
    import urllib
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(600): break
        from resources.zattooDB import ZattooDB
        _zattooDB_ = ZattooDB()
        #update programInfo    
        startTime=datetime.datetime.now()
        endTime=datetime.datetime.now()+datetime.timedelta(minutes = 20)
        print 'StartRefresh  ' + str(datetime.datetime.now())
        try:
            _zattooDB_.getProgInfo(False, startTime, endTime)
        except:
            print 'ERROR on REFRESH'
            pass
        print "REFRESH Prog  " + str(datetime.datetime.now())

def recInfo():
    import urllib
    
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist', None)
    if resultData is None: return
    for record in resultData['recordings']:
        _zattooDB_.getShowInfo(record['program_id'])  
           
def start():
    import urllib
    
    _zattooDB_.cleanProg()
    _zattooDB_.updateChannels()
    _zattooDB_.updateProgram()
    
    startTime=datetime.datetime.now()#-datetime.timedelta(minutes = 60)
    endTime=datetime.datetime.now()+datetime.timedelta(minutes = 20)
    
    
    xbmcgui.Dialog().notification(localString(31916), localString(30110),  __addon__.getAddonInfo('path') + '/icon.png', 3000, False) 
    _zattooDB_.getProgInfo(True, startTime, endTime)
    
    xbmcgui.Dialog().notification(localString(31106), localString(31915),  __addon__.getAddonInfo('path') + '/icon.png', 3000, False) 
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    recInfo()
    _library_.delete_library() # add by samoth
    _library_.make_library()   
    xbmc.executebuiltin("Dialog.Close(busydialog)")

    refreshProg()  



if __addon__.getSetting('dbonstart') == 'true': start()
print "No DB--SERVICE"



