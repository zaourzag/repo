#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcvfs
import json,urllib2,re,urlparse,os
import pyxbmct
import requests,cookielib
from difflib import SequenceMatcher
import time,datetime


try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

   
cachezeit=24  
cache = StorageServer.StorageServer("context.serieninfos", cachezeit) # (Your plugin name, Cache time in hours

addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
session = requests.session()

if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
  
def geturl(url,data="x",header=""): 
   
    headers = {'User-Agent':         'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0', 
    }        
    ip=addon.getSetting("ip")
    port=addon.getSetting("port")    
    if not ip=="" and not port=="":
      px="http://"+ip+":"+str(port)
      proxies = {
        'http': px,
        'https': px,
      }    
      content = session.get(url, allow_redirects=True,verify=False,headers=headers,proxies=proxies)    
    else:
      content = session.get(url, allow_redirects=True,verify=False,headers=headers)    
    return content.text


    
class Infowindow(pyxbmct.AddonDialogWindow):
    text=""
    pos=0
    def __init__(self, title='',text='',image="",lastplayd_title="",lastepisode_name="",fehlen=""):
        super(Infowindow, self).__init__(title)
        self.setGeometry(600,600,16,8)        
        self.bild=image
        self.text=text    
        self.lastplayd_title=lastplayd_title
        self.lastepisode_name=lastepisode_name
        self.fehlen=fehlen
        self.set_info_controls()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_info_controls(self):
      self.image = pyxbmct.Image(self.bild)
      self.placeControl(self.image, 0, 0,columnspan=8,rowspan=3)
      if not fehlen=="":
         x=0
      else:
         x=1
      self.textbox=pyxbmct.TextBox()       
      self.placeControl(self.textbox, 3, 0, columnspan=8,rowspan=11+x)                       
      self.textbox.setText(self.text)
      if not fehlen=="":
        self.textboxf=pyxbmct.TextBox()                  
        self.placeControl(self.textboxf, 14, 0, columnspan=8,rowspan=1)                       
        self.textboxf.setText("Fehlende Folgen : "+ fehlen)
      
      self.textbox2=pyxbmct.TextBox()                  
      self.placeControl(self.textbox2, 15, 0, columnspan=4,rowspan=1)                       
      self.textbox2.setText("Letze Gesehene : "+ lastplayd_title)
      
      self.textbox3=pyxbmct.TextBox()            
      self.placeControl(self.textbox3, 15, 5, columnspan=3,rowspan=1)                       
      self.textbox3.setText("Vorhanden Bis : "+ lastepisode_name)      

      self.connectEventList(
             [pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_UP],
            self.hoch)         
      self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN],
            self.runter)                  
      self.setFocus(self.textbox)            
    def hoch(self):
        self.pos=self.pos-1
        if self.pos < 0:
          self.pos=0
        self.textbox.scroll(self.pos)
    def runter(self):
        self.pos=self.pos+1        
        self.textbox.scroll(self.pos)
        posnew=self.textbox.getPosition()
        debug("POSITION : "+ str(posnew))


        

def gettitle()  :
  title=""
  title=xbmc.getInfoLabel('ListItem.TVShowTitle')
  try:    
    info = sys.listitem.getVideoInfoTag() 
    title=info.getTVShowTitle()
  except:
    pass
  try:
      title=xbmc.getInfoLabel('ListItem.TVShowTitle')
  except:
       pass
  if title=="":
     title = xbmc.getInfoLabel("ListItem.Title").decode('UTF-8')      
  if title=="":
     title=sys.listitem.getLabel()
  debug("TITLE :::: "+title)     
  return title

def get_episodedata(title):
  query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "filter": { "field": "tvshow", "operator": "is", "value": "" }, "limits": { "start" : 0 }, "properties": ["playcount", "runtime", "tvshowid","episode","season"], "sort": { "order": "ascending", "method": "label" } }, "id": "libTvShows"}
  query = json.loads(json.dumps(query))
  query['params']['filter']['value'] = title
  response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
  
  lastplayd_nr=0
  lastplayd_title=""
  lastplayd_staffel=1
  lastepisode_nr=0
  lastepisode_name="" 
  lastepisode_staffel=1
  fehlen=""
  try:
    for episode in response["result"]["episodes"]:
      debug("------")
      debug (episode)
      if episode["playcount"] > 0:
        if lastplayd_nr<episode["episode"] or lastplayd_staffel<episode["season"]:
          lastplayd_nr=episode["episode"]
          lastplayd_staffel=episode["season"]
          lastplayd_title="S"+str(episode["season"])+"E"+str(episode["episode"])
            
      if lastepisode_nr<episode["episode"] or lastepisode_staffel<episode["season"] :
        if lastepisode_staffel<episode["season"]:
          lastepisode_nr=0            
        count=episode["episode"]-lastepisode_nr
        if count>1:
          debug("lastepisode_nr :"+str(lastepisode_nr))
          debug("episode :"+str(episode["episode"]))
          if count==2:
            fehlen=fehlen+","+"S"+str(episode["season"])+"E"+str(lastepisode_nr+1)              
          if count >2:
            fehlen=fehlen+","+"S"+str(lastepisode_staffel)+"E"+ str(lastepisode_nr+1) +" - "+ "S"+str(episode["season"])+"E"+str(episode["episode"]-1)
               
        lastepisode_nr=episode["episode"]
        lastepisode_name="S"+str(episode["season"])+"E"+str(episode["episode"])
        lastepisode_staffel=episode["season"] 
    if len(fehlen) >0:
      fehlen=fehlen[1:]
      debug("lastplayd_title : "+lastplayd_title) 
      debug("lastepisode_name : "+lastepisode_name) 
      debug("fehlen : "+fehlen) 
  except:
    pass

  return lastplayd_title,lastepisode_name,fehlen
def fixtime(date_string,format):
    debug("date_string,format :" +str(date_string)+","+str(format))
    try:
        x=datetime.datetime.strptime(date_string, format)
    except TypeError:
        x=datetime.datetime(*(time.strptime(date_string, format)[0:6]))  
    return x
    
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
def getallfolgen(idd):
    url="https://api.themoviedb.org/3/tv/"+str(idd)+"?api_key=f5bfabe7771bad8072173f7d54f52c35&language=en_US"
    debug("getallfolgen url : "+url)    
    content = cache.cacheFunction(geturl,url) 
    structure = json.loads(content)
    debug(structure)
    now = datetime.datetime.now()      
    last = fixtime("1900-01-01", "%Y-%m-%d")
    next = fixtime("2200-01-01", "%Y-%m-%d")
    lastdatum=""
    lastepisode=""
    nextepisode=""
    nextdatum=""
    for season in structure["seasons"]:        
       nr=season["season_number"]
       if int(nr)==0:
         continue
       seasonurl="https://api.themoviedb.org/3/tv/"+str(idd)+"/season/"+str(nr)+"?api_key=f5bfabe7771bad8072173f7d54f52c35&language=en_US"
       debug("seasonurl : "+seasonurl)       
       content2 = cache.cacheFunction(geturl,seasonurl) 
       structure= json.loads(content2) 
       debug(structure)
       for episode in structure["episodes"]:
        debug(episode)
        datum=episode["air_date"]
        nummer=episode["episode_number"]
        season=episode["season_number"]
        try:
            date1 = fixtime(datum, "%Y-%m-%d")      
            if date1> now and date1<next:
                nextdatum=datum
                nextepisode="S"+str(season)+"E"+str(nummer)
                next=date1
            if date1< now and date1>last:
                lastdatum=datum
                lastepisode="S"+str(season)+"E"+str(nummer)
                last=date1          
            debug(datum +" : S"+str(season)+"E"+str(nummer))
        except:
            pass        
    debug("LAST: "+ lastdatum+" "+lastepisode)
    debug("Next: "+ nextdatum+" "+nextepisode)
    return (nextdatum,nextepisode,lastdatum,lastepisode)
        
       
       

addon = xbmcaddon.Addon()    
debug("Hole Parameter")
debug("Argv")
debug(sys.argv)
debug("----")
try:
      params = parameters_string_to_dict(sys.argv[2])
      mode = urllib.unquote_plus(params.get('mode', ''))
      series = urllib.unquote_plus(params.get('series', ''))
      season = urllib.unquote_plus(params.get('season', ''))
      debug("Parameter Holen geklappt")
except:
      debug("Parameter Holen nicht geklappt")
      mode="" 
debug("Mode ist : "+mode)
if mode=="":      
    title=gettitle()
    lastplayd_title,lastepisode_name,fehlen=get_episodedata(title)    
    title=re.sub('\(.+?\)', '', title)
    url="https://api.themoviedb.org/3/search/tv?api_key=f5bfabe7771bad8072173f7d54f52c35&language=de-DE&query=" + title.replace(" ","+")
    debug("Searchurl "+url)    
    content = cache.cacheFunction(geturl,url) 
    wert = json.loads(content)  
    
    count=0
    gefunden1=0
    gefunden2=0
    wertnr1=0
    wertnr2=0
    x1=0
    x2=0
    x=0
    for serie in wert["results"]:
      serienname1=serie["original_name"].encode("utf-8")
      serienname2=serie["name"].encode("utf-8")
      debug("serienname2 :"+serienname2)
      debug("serienname1 :"+serienname1)
      nummer1=similar(title,serienname1)     
      nummer2=similar(title,serienname2)  
      if nummer1 >wertnr1:
            wertnr1=nummer1
            gefunden1=count
            x1=1
      if nummer2 >wertnr2:       
            wertnr2=nummer2
            gefunden2=count     
            x2=1
      count+=1
    debug("#######")
    debug(wertnr2)
    debug(wertnr1)
    debug("#######")
    if float(wertnr2) > float(wertnr1):
        x=x2
        gefunden=gefunden2
    else:
        x=x1
        gefunden=gefunden1
    debug("X :"+ str(x))
    debug("gefunden :"+ str(gefunden))
    debug("1. +++suche++"+title)
    debug(wert)
    if x==0:
      dialog = xbmcgui.Dialog()
      ok = dialog.ok('Nicht gefunden', 'Serie Nicht gefunden')
      quit()
    debug("_****_") 
    debug(gefunden)
    idd=wert["results"][gefunden]["id"]
    debug("IDD: "+str(idd))
    seriesName=wert["results"][gefunden]["name"]
    serienstart=wert["results"][gefunden]["first_air_date"]
    (nextdatum,nextfolge,lastdatum,lastfolge)=getallfolgen(idd)
    #wert1=tvdb.get_last_episode_for_series(idd)
    #debug("2. ++++last+++")
    #debug(wert1)
    leztefolge=lastfolge
        
    debug("3. ++++++serie++++")    
    debug(serie)    
    try:
        Bild="http://image.tmdb.org/t/p/w300/"+wert["results"][gefunden]["backdrop_path"].encode("utf-8")
    except:
        Bild=""
    debug("Bild :"+Bild)
    serienurl="https://api.themoviedb.org/3/tv/"+str(idd)+"?api_key=f5bfabe7771bad8072173f7d54f52c35&language=de-DE"
    debug("serienurl : "+serienurl)    
    content_serie = cache.cacheFunction(geturl,serienurl) 
    struct_serie = json.loads(content_serie)      
    status=struct_serie["status"].decode("utf-8")
    statustext="Der Status der Serie ist : "+status
    if status=="Returning Series":
      statustext="Status:         läuft".decode("utf-8")
    if status=="Canceled":
      statustext="Status:         Abgesetzt"
    if status=="Ended":
        statustext="Status:         Beendet"            
    #Continuing
    try:
      sender= struct_serie["Networks"][0].decode("utf-8")
    except:
       sender=""
    if sender=="":
       sendertext=""
    else:
       sendertext="Sender:         "+sender
    titlesuche = struct_serie["name"]
    try:
      nextfolge=nextfolge
    except:
       nextfolge=""
    if nextfolge=="":
      textnext="Naechste Folge: \n"
    else:
       textnext="Naechste Folge: \nUS :"+nextfolge+" ("+nextdatum+" )"       
    
    eidurl="https://api.themoviedb.org/3/tv/"+str(idd)+"/external_ids?api_key=f5bfabe7771bad8072173f7d54f52c35&language=de-DE"
    debug("eidurl : "+eidurl)    
    content = cache.cacheFunction(geturl,eidurl) 
    wwert = json.loads(content)  
    tvdbid=wwert["tvdb_id"]
    
    getnextde="https://tvdb.cytec.us/api/8XYAYYQTIAHQSBJQ/series/"+str(tvdbid)+"/all/de.json"    
    debug(getnextde)    
    try:
        content = cache.cacheFunction(geturl,getnextde) 
        struktur = json.loads(content)
    except:
        content = geturl(getnextde) 
    debug("------>")
    debug(content)
    try:
        struktur = json.loads(content)  
        episoden=struktur["Data"]["Episode"]
        desender=struktur["Data"]["Series"]["Network"]
        if "Amazon" in desender:
           desender="Amazon"
        dezeit=struktur["Data"]["Series"]["Airs_Time"]    
        now = time.time()
        next=5000000000        
        last=0
        next_EpisodeNumber=""
        next_SeasonNumber=""
        last_EpisodeNumber=""
        last_SeasonNumber=""
        for episode in episoden:
            try:
                start=episode["FirstAired"]  
                debug(start)        
                mit=time.strptime(start, "%Y-%m-%d")
                debug(mit)              
                starttime=time.mktime(mit)
            except:
                starttime=0
            debug(starttime)
            debug(now)
            debug("##--##")
            if starttime>now:
                if starttime<next:
                    next=starttime
                    next_EpisodeNumber=episode["EpisodeNumber"] 
                    next_SeasonNumber=episode["SeasonNumber"] 
            if starttime<now:
                if starttime>last:
                    last=starttime
                    last_EpisodeNumber=episode["EpisodeNumber"] 
                    last_SeasonNumber=episode["SeasonNumber"]           
        if next < 5000000000:
            nextde=datetime.datetime.fromtimestamp(next).strftime("%d/%m/%Y")
            de_next="  De : "+next_SeasonNumber+"X"+next_EpisodeNumber+". ( "+nextde+" "+ dezeit +" "+desender +" )\n"
        else:
            de_next="\n"   
        if last >0:
            lastde=datetime.datetime.fromtimestamp(last).strftime("%d/%m/%Y")
            de_last="  De : "+last_SeasonNumber+"X"+last_EpisodeNumber+". ( "+lastde+" "+ dezeit +" "+desender +" )\n"
        else:
            de_last="\n"                      
    except:
       de_last="\n"
       de_next="\n"
    debug("5.++++++SUM++++++++")
    zusatz=""
    anzahLstaffeln=int(struct_serie["number_of_seasons"])
    for season in struct_serie["seasons"]:           
        zusatz= zusatz+" "+str(season["name"])+ ": "+ str(season["episode_count"])+ " Folgen\n"
    
    Zusammenfassung="Serienname: "+seriesName+"\nSerienstart : "+serienstart +"\nAnzahl Staffeln : "+str(anzahLstaffeln)+"\n"+statustext+u"\n"+"Letzte Folge: \nUS : "+leztefolge+" ( "+lastdatum+" )"+de_last+textnext+de_next+zusatz
    window = Infowindow(title="Serieninfo",text=Zusammenfassung,image=Bild,lastplayd_title=lastplayd_title,lastepisode_name=lastepisode_name,fehlen=fehlen)
    window.doModal()
    del window

    
    
