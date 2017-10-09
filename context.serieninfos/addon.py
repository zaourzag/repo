#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcvfs
import json,urllib2,re,urlparse,os
import pyxbmct
import requests,cookielib
from thetvdb import TheTvDb
from difflib import SequenceMatcher
import time,datetime

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
  
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


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
    tvdb = TheTvDb("de-DE")
    wert=tvdb.search_series(title.decode("utf-8"))
    count=0
    gefunden=0
    wertnr=0
    x=0
    for serie in wert:
      serienname=serie["seriesName"]
      nummer=similar(title,serienname)      
      if nummer >=wertnr:
        wertnr=nummer
        gefunden=count
        x=1
      count+=1
    debug("1. +++suche++"+title)
    debug(wert)
    if x==0:
      dialog = xbmcgui.Dialog()
      ok = dialog.ok('Nicht gefunden', 'Serie Nicht gefunden')
      quit()
    idd=wert[gefunden]["id"]
    seriesName=wert[gefunden]["seriesName"]
    serienstart=wert[gefunden]["firstAired"]
    wert1=tvdb.get_last_episode_for_series(idd)
    debug("2. ++++last+++")
    debug(wert1)
    leztefolge=wert1["airdate.label"].decode("utf-8")
    
    serie=tvdb.get_series(idd)
    debug("3. ++++++serie++++")    
    debug(serie)
    Bild=serie["art"]["banner"]
    status=serie["status"].decode("utf-8")
    statustext="Der Status der Serie ist : "+status
    if status=="Continuing":
      statustext="Status:         läuft".decode("utf-8")
    if status=="Ended":
      statustext="Status:         Abgesetzt"
    #Continuing
    try:
      sender= serie["studio"][0].decode("utf-8")
    except:
       sender=""
    if sender=="":
       sendertext=""
    else:
       sendertext="Sender:         "+sender
    titlesuche = serie["title"].decode("utf-8")
    
    next=tvdb.get_nextaired_episode(idd)
    debug("4. ++++++next+++")
    debug(next)
    try:
      nextfolge=next["airdate.label"].decode("utf-8")
    except:
       nextfolge=""
    if nextfolge=="":
      textnext=""
    else:
       textnext="Naechste Folge: \nUS :"+nextfolge+"\n"
    getnextde="https://tvdb.cytec.us/api/8XYAYYQTIAHQSBJQ/series/"+str(idd)+"/all/de.json"    
    debug(getnextde)
    content=geturl(getnextde)
    debug("------>")
    debug(content)
    struktur = json.loads(content)  
    episoden=struktur["Data"]["Episode"]
    desender=struktur["Data"]["Series"]["Network"]
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
       de_next="De: "+next_SeasonNumber+"X"+next_EpisodeNumber+". ( "+nextde+" "+ dezeit +" "+desender +" )\n"
    else:
       de_next=""   
    if next >0:
       lastde=datetime.datetime.fromtimestamp(last).strftime("%d/%m/%Y")
       de_last="De: "+last_SeasonNumber+"X"+last_EpisodeNumber+". ( "+lastde+" "+ dezeit +" "+desender +" )\n"
    else:
       de_last=""                  
    summ=tvdb.get_series_episodes_summary(idd)
    debug("5.++++++SUM++++++++")
    debug(summ)
    anzahLstaffeln = int(sorted(summ["airedSeasons"],key=int)[-1])
    debug(anzahLstaffeln)
    #anzahLstaffeln=len(summ["airedSeasons"])
    Seasons=[]
    zusatz=""
    counter=0
    for i in range(0,anzahLstaffeln+1):        
       query="airedSeason=%s" % i
       season=tvdb.get_series_episodes_by_query(idd, query)
       debug("6.++++++Season++++++++"+str(i))
       debug(season)

       anz=len(season)
       if not anz==0:
        if counter%2 == 0:
            zusatz=zusatz+"\n"
        else:
            zusatz=zusatz+"          "
        zusatz= zusatz+" Staffel "+str(i)+ ": "+ str(anz)+ " Folgen"
        counter+=1
    
    Zusammenfassung="Serienname: "+seriesName+"\nSerienstart : "+serienstart +"\nAnzahl Staffeln : "+str(anzahLstaffeln)+"\n"+statustext+u"\n"+"Letzte Folge: \nUS: "+leztefolge+"\n"+de_last+textnext+de_next+zusatz
    window = Infowindow(title="Serieninfo",text=Zusammenfassung,image=Bild,lastplayd_title=lastplayd_title,lastepisode_name=lastepisode_name,fehlen=fehlen)
    window.doModal()
    del window

    
    
