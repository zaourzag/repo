# coding=utf-8
#
#    copyright (C) 2017 Steffen Rolapp (github@rolapp.de)
#
#    This file is part of ZattooBox
#
#    ZattooBox is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    ZattooBox is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with ZattooBox.  If not, see <http://www.gnu.org/licenses/>.
#


import xbmc, xbmcgui, xbmcaddon, datetime, time
import os, urlparse
from resources.library import library 
from resources.zattooDB import ZattooDB
_zattooDB_ = ZattooDB()          
__addon__ = xbmcaddon.Addon()
_library_=library()
localString = __addon__.getLocalizedString
SWISS = __addon__.getSetting('swiss')
              
def refreshProg():
    import urllib
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(600): break
        from resources.zattooDB import ZattooDB
        _zattooDB_ = ZattooDB()
        #update programInfo    
        startTime=datetime.datetime.now()
        endTime=datetime.datetime.now()+datetime.timedelta(minutes = 120)
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
    
    if SWISS == 'true':
        xbmcgui.Dialog().notification(localString(31106), localString(31915),  __addon__.getAddonInfo('path') + '/icon.png', 3000, False) 
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        recInfo()
        _library_.delete_library() # add by samoth
        _library_.make_library()   
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    
        refreshProg()  



if __addon__.getSetting('dbonstart') == 'true': start()
print "No DB--SERVICE"



