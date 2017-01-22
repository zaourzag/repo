# coding=utf-8
#
#    ZattooBox Extended
#
#  Record -Library
#


import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, urlparse
import  time, datetime, threading
from resources.zattooDB import ZattooDB

__addon__ = xbmcaddon.Addon()
__addonId__=__addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
_zattooDB_ = ZattooDB()

class library:
  
  def make_library(self):
    folder=__addon__.getSetting('library_dir')
    if not folder: return
    import os
    libraryPath = xbmc.translatePath(folder)
    if not os.path.exists(libraryPath): os.makedirs(libraryPath)
    
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist', None)
    if resultData is None: return
    for record in resultData['recordings']:
      showInfo=_zattooDB_.getShowInfo(record['program_id'])
      
      if showInfo == "NONE": continue
      
      if showInfo['episode_title']: name=showInfo['title']+'-'+showInfo['episode_title']
      else: name=showInfo['title']
  
      fileName=slugify(name)
      strmFile=os.path.join(libraryPath, fileName+"/"+fileName+".strm")
      if os.path.exists(os.path.dirname(strmFile)):continue
      
      os.makedirs(os.path.dirname(strmFile))
      f = open(strmFile,"w")
      f.write('plugin://'+__addonId__+'/?mode=watch_r&id='+str(record['id']))
      f.close()
      
      out='<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><movie>'
      out+='<title>'+name+' [COLOR red]ZBE[/COLOR]</title>'
      out+='<year>'+str(showInfo['year'])+'</year>'
      out+='<plot>'+showInfo['description']+'</plot>'
      out+='<thumb>'+showInfo['image_url']+'</thumb>'
      out+='<fanart><thumb>'+showInfo['image_url']+'</thumb></fanart>'
      for genre in showInfo['genres']:
        out+='<genre>'+genre+'</genre>'
      for cr in showInfo['credits']:
        role=cr['role']
        if role=='actor':out+='<actor><name>'+cr['person']+'</name></actor>'
        else: out+='<'+role+'>'+cr['person']+'</'+role+'>'
      out+='</movie>'
      
      nfoFile=os.path.join(libraryPath, fileName+"/"+fileName+".nfo")
      f = open(nfoFile,"w")
      f.write(out.encode("UTF-8"))
      f.close()
    xbmcgui.Dialog().notification('Ordner für Filme aktualisiert', __addon__.getLocalizedString(31251),  __addon__.getAddonInfo('path') + '/icon.png', 5000, False)    

# added - by Samoth  
  def delete_library(self): 
    folder=__addon__.getSetting('library_dir') 
    if not folder: return 
    import os, shutil 
    libraryPath = xbmc.translatePath(folder) 
    if os.path.exists(libraryPath) and libraryPath != "": 
      shutil.rmtree(libraryPath)  
      
# added - by Samoth
  def delete_entry_from_library(self, recording_id): 
    import os, shutil 
    folder=__addon__.getSetting('library_dir') 
    if not folder: return 
    libraryPath = xbmc.translatePath(folder)
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist', None) 
    for record in resultData['recordings']: 
      if recording_id == str(record['id']): 
        showInfo=_zattooDB_.getShowInfo(record['program_id']) 
        if showInfo == "NONE": continue 
        
        if showInfo['episode_title']: name=showInfo['title']+'-'+showInfo['episode_title'] 
        else: name=showInfo['title'] 
  
        fileName=slugify(name) 
        strmDir=os.path.join(libraryPath, fileName) 
        if os.path.exists(os.path.dirname(strmDir)): 
         shutil.rmtree(strmDir) 
        continue 
        
        
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import re, unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value
  
