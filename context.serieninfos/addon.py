#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcvfs
import json,cookielib,urllib2,re,urlparse,os
import pyxbmct
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from datetime import datetime    
import urllib

addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       
cookie=temp+"/cookie.jar"
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)


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
		paramPairs = parameters[0:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
  
def geturl(url,data="x",header=""):
        global cj
        print("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]        
        else:
          opener.addheaders = header        
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        return content


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
    
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

def parseserie(name,sstaffel=0) :
  newlink="http://www.serienjunkies.de"+name+"alle-serien-staffeln.html"
  debug("URL :"+newlink)
  content=geturl(newlink)            
  
  htmlPage = BeautifulSoup(content, 'html.parser')
  searchitem = htmlPage.find("p",class_="box clear pad5")
  debug("-----_")
  Zusammenfassung=searchitem.text.encode('utf-8').decode('ascii', 'ignore')
  
  debug("########## "+Zusammenfassung)
  searchitem = htmlPage.find("table", attrs={'id':'epsum'})
  rows = searchitem.find_all('tr')
  staffel_arr=[]
  folgen_arr=[]
  deutsch_arr=[]
  englisch_arr=[]
  for row in rows:
    cols = row.find_all('td')
    spalte=0
    for col in cols:  
      cont=col.text 
      if spalte==0:
         Staffelnummer = re.compile('Staffel ([0-9]+)', re.DOTALL).findall(cont)[0]
         staffel_arr.append(Staffelnummer)
      if spalte==1:
         folgen_arr.append(cont)
      if spalte==2:
         deutsch_arr.append(cont)
      if spalte==3:
         englisch_arr.append(cont)
      spalte=spalte+1     
      
  searchitem = htmlPage.find("meta",attrs={'property':'og:image'})
  image=searchitem['content']
  
  searchitem = htmlPage.find("table", attrs={'class':'eplist'})
  rows = searchitem.find_all('tr')
  folge_arr=[]
  de_datum_arr=[]
  de_name_arr=[]
  en_datum_arr=[]
  en_name_arr=[]
  
  for row in rows:
    cols = row.find_all('td')
    for spalte in range(0,4,1):
      try:           
        cont=cols[spalte].text.encode('utf-8').decode('ascii', 'ignore') 
      except:
         cont=""
      if spalte==0:
         folge_arr.append(cont)
      if spalte==1:
         en_datum_arr.append(cont)
      if spalte==2:
         en_name_arr.append(cont)
      if spalte==3:
         de_name_arr.append(cont)
      if spalte==4:
         de_datum_arr.append(cont)         
  lastst=""      
  now=datetime.today()  
  if int(sstaffel) > 0:        
    for i in range(0,len(en_name_arr),1):     
      try:        
        if folge_arr[i].startswith(str(sstaffel)+"x"):
            mydate = datetime.strptime(en_datum_arr[i], "%d.%m.%Y")
            if not "TBA" in en_name_arr[i] and mydate < now:
                  lastst=folge_arr[i]
            else:          
              break
      except:
         pass         
  else:
     lastst="-1"  
  lf=""  
  for i in range(0,len(en_name_arr),1):     
      try:
         mydate = datetime.strptime(en_datum_arr[i], "%d.%m.%Y")
         if not "TBA" in en_name_arr[i] and mydate < now :
           lf=folge_arr[i]
         else:
            break
      except:
         pass
  if "Episoden eingestellt." in Zusammenfassung:
    ende=1
  else: 
    ende=0
  return (image,Zusammenfassung,staffel_arr,folgen_arr,lf,lastst,ende)


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

def changetitle(title):
     
    suchtitle=title.replace(" ","+")
    suchtitle=suchtitle.replace("'","")
    try:
      suchtitle2 = re.compile('(.+?)\+\([0-9]+\)', re.DOTALL).findall(suchtitle)[0]     
      suchtitle=suchtitle2
    except:
      pass    
   
    xc=geturl("http://www.serienjunkies.de/suchen.php")
    url="http://www.serienjunkies.de/suchen.php?s="+suchtitle+"+XXXX&a=s&t=0"    
    debug("URL :"+url)
    content=geturl(url)
    
    match = re.compile('<div class="sminibox"><a href="(.+?)"><img src="(.+?)"[^"]+?alt="(.+?)"/>', re.DOTALL).findall(content)
    maxlink=""
    maxnr=0
    for link,image,name in match:
      name_comp=name.replace(" ","")
      try:
        name_comp1 = re.compile('(.+?)\([0-9]+\)', re.DOTALL).findall(name_comp)[0]
        name_comp=name_comp1
      except:
         pass
      title_comp=title.replace(" ","")
      try:
        title_comp1 = re.compile('(.+?)\([0-9]+\)', re.DOTALL).findall(title_comp)[0]
        title_comp=title_comp1
      except:
         pass
      xy=similar(title_comp,name_comp)
      if xy>0.8:
          if xy>maxnr:
            maxnr=xy
            maxlink=link
          debug("Treffer")
      else:
           debug("Kein Treffer")
      debug("name_comp :"+name_comp)
      debug("title_comp : "+title_comp)
      debug("#############" + str(xy))
    debug("maxlink : "+maxlink)        
    return maxlink

addon = xbmcaddon.Addon()    
try:
      params = parameters_string_to_dict(sys.argv[1])
      debug("1")
      debug(params)
      mode = urllib.unquote_plus(params.get('mode', ''))
      debug("2")
      series = urllib.unquote_plus(params.get('series', ''))
      debug("3")
      season = urllib.unquote_plus(params.get('season', ''))
      debug("4")
except:
      mode="" 
debug("Mode :")
debug(mode)
debug(sys.argv[1])
if mode=="":      
    title=gettitle()
    lastplayd_title,lastepisode_name,fehlen=get_episodedata(title)
    debug("####### :"+lastplayd_title)
    maxlink= changetitle(title)
    if maxlink=="":
      xbmc.executebuiltin('Notification('+title+',"Serie nicht gefunden")')
    else:      
      Bild,Zusammenfassung,staffel_arr,folgen_arr,letztefolge,this_staffel,ende=parseserie(maxlink,sstaffel=0) 
      for i in range(0,len(staffel_arr),1):
        if i%2 == 0:
          Zusammenfassung=Zusammenfassung+"\n"
        else:
          Zusammenfassung=Zusammenfassung+"          "
        Zusammenfassung= Zusammenfassung+" Staffel "+staffel_arr[i]+ ": "+ folgen_arr[i]+ " Folgen"    
    debug("Letzte Folge :" +str(letztefolge))
    debug("this_staffel Folge :" +str(this_staffel))
    debug("Zuende :" +str(ende))
    window = Infowindow(title="SerienFino",text=Zusammenfassung,image=Bild,lastplayd_title=lastplayd_title,lastepisode_name=lastepisode_name,fehlen=fehlen)
    window.doModal()
    del window
    if mode=="fetch":
       pass
if mode=="getseries":
    debug("getseries")
    lastplayd_title,lastplayd_title,fehlen=get_episodedata(series)
    maxlink= changetitle(series)         
    Bild,Zusammenfassung,staffel_arr,folgen_arr,letztefolge,this_staffel,ende=parseserie(maxlink,sstaffel=season)
    debug("Bild :"+Bild)
    # Window ID
    WINDOW = xbmcgui.Window(12902)
    #WINDOW.clearProperties()
    WINDOW.setProperty('Bild',Bild)
    WINDOW.setProperty('Zusammenfassung',Zusammenfassung)
    for i in range(0,len(staffel_arr),1):
      WINDOW.setProperty('staffel'+str(i),folgen_arr[i])
    WINDOW.setProperty('letztefolge',letztefolge)
    WINDOW.setProperty('this_staffel',this_staffel)
    WINDOW.setProperty('ende',str(ende))
    WINDOW.setProperty('fehlen',fehlen)
    xxxxxx = WINDOW.getProperty('Bild')
    debug("XXXXX" +xxxxxx)
    
    
    
cj.save(cookie,ignore_discard=True, ignore_expires=True)