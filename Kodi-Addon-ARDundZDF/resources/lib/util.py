# -*- coding: utf-8 -*-
# util.py
#	

import os, sys, glob, shutil, time
import datetime as dt	# für xml2srt
import urllib, urllib2, ssl
# import requests		# kein Python-built-in-Modul, urllib2 verwenden
from StringIO import StringIO
import gzip, zipfile
from urlparse import parse_qsl
import base64 			# url-Kodierung für Kontextmenüs
import json				# json -> Textstrings
import pickle			# persistente Variablen/Objekte
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
	
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

# Globals
NAME			= 'ARD und ZDF'
KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

DEBUG			= SETTINGS.getSetting('pref_info_debug')

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
SUBTITLESTORE 	= os.path.join("%s/subtitles") % ADDON_DATA
TEXTSTORE 		= os.path.join("%s/Inhaltstexte") % ADDON_DATA
WATCHFILE		= os.path.join("%s/merkliste.xml") % ADDON_DATA
TEMP_ADDON		= xbmc.translatePath("special://temp")			# Backups

PLAYLIST 		= 'livesenderTV.xml'		# TV-Sender-Logos erstellt von: Arauco (Plex-Forum). 											
ICON_MAIN_POD	= 'radio-podcasts.png'
ICON_MAIN_ZDFMOBILE		= 'zdf-mobile.png'
			
BASE_URL 		= 'https://classic.ardmediathek.de'

###################################################################################################
#									Hilfsfunktionen Kodiversion
#	Modulnutzung: 
#					import resources.lib.util as util
#					PLog=util.PLog;  home=util.home; ...  (manuell od.. script-generiert)
#
#	convert_util_imports.py generiert aus util.py die Zuordnungen PLog=util.PLog; ...
####################################################################################################
#----------------------------------------------------------------  
def PLog(msg, loglevel=xbmc.LOGDEBUG):
	if DEBUG == 'false':
		return
	if isinstance(msg, unicode):
		msg = msg.encode('utf-8')
	loglevel = xbmc.LOGNOTICE
	# PLog('loglevel: ' + str(loglevel))
	if loglevel >= 2:
		xbmc.log("%s --> %s" % ('ARDundZDF', msg), level=loglevel)
#---------------------------------------------------------------- 

# Home-Button, Aufruf: item = home(item=item, ID=NAME)
#	Liste item von Aufrufer erzeugt
def home(li, ID):												
	PLog('home: ' + str(ID))	
	title = 'Zurück zum Hauptmenü ' + str(ID)
	summary = title
	
	CurSender = Dict("load", 'CurSender')		
	CurSender = UtfToStr(CurSender)
	PLog(CurSender)	
	
	if ID == NAME:		# 'ARD und ZDF'
		name = 'Home : ' + NAME
		fparams="&fparams={}"
		addDir(li=li, label=name, action="dirList", dirID="Main", fanart=R('home.png'), 
			thumb=R('home.png'), fparams=fparams)
			
	if ID == 'ARD':
		name = 'Home: ' + "ARD Mediathek Classic"
		# CurSender = Dict("load", "CurSender")	# entf.  bei Classic
		fparams="&fparams={'name': '%s', 'sender': '%s'}"	% (urllib2.quote(name), '')
		addDir(li=li, label=title, action="dirList", dirID="Main_ARD", fanart=R('home-ard-classic.png'), 
			thumb=R('home-ard-classic.png'), fparams=fparams)
		
	if ID == 'ARD Neu':
		name = 'Home: ' + "ARD Mediathek"
		CurSender = Dict("load", "CurSender")
		fparams="&fparams={'name': '%s', 'CurSender': '%s'}"	% (urllib2.quote(name), urllib2.quote(CurSender))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Main_NEW", 
			fanart=R('home-ard.png'), thumb=R('home-ard.png'), fparams=fparams)
			
	if ID == 'ZDF':
		name = 'Home: ' + "ZDF Mediathek"
		fparams="&fparams={'name': '%s'}" % urllib2.quote(name)
		addDir(li=li, label=title, action="dirList", dirID="Main_ZDF", fanart=R('home-zdf.png'), 
			thumb=R('home-zdf.png'), fparams=fparams)
		
	if ID == 'ZDFmobile':
		name = 'Home :' + "ZDFmobile"
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.Main_ZDFmobile", 
			fanart=R(ICON_MAIN_ZDFMOBILE), thumb=R(ICON_MAIN_ZDFMOBILE), fparams=fparams)
			
	if ID == 'PODCAST':
		name = 'Home :' + "Radio-Podcasts"
		fparams="&fparams={'name': '%s'}" % urllib2.quote(name)
		addDir(li=li, label=title, action="dirList", dirID="Main_POD", fanart=R(ICON_MAIN_POD), 
			thumb=R(ICON_MAIN_POD), fparams=fparams)

	return li
	 
#---------------------------------------------------------------- 
#	03.04.2019 data-Verzeichnis des Addons:
#  		Check /Initialisierung / Migration
#	Die Funktion checkt bei jedem Aufruf des Addons das data-Verzeichnis
#		auf Existenz. Bis Version 1.3.9  befand sich das data-Verzeichnis
#		innerhalb des Addons., das neue außerhalb in: 
#		../plugin.video.ardundzdf/resources/data
#	Existiert das data-Verzeichnis beim Check nicht, wird das alte data-
#		Verzeichnis migriert. Ein Backup wird im "special://temp"-Ordner 
#		angelegt (data.zip).
#		Existiert kein altes data-Verzeichnis, wird ein leeres neues
#		angelegt.
#	Bereinigung nach Migration:
#		Für das alte  data-Verzeichnis ist ein Löschen im Rahmen der 
#		Addon-Updates vorgesehen (git rm resources/data).
#		Für das Backup data.zip ist kein Löschen vorgesehen.
#	 
def check_DataStores():
	PLog('check_DataStores:')
	OLDSTORE 		= os.path.join("%s/resources/data") % ADDON_PATH
	OLDPATH 		= os.path.join("%s/resources") % ADDON_PATH
				
	#	Check / Ankündigung Migration
	#			ohne altes data-Verzeichnis: leeres neues
	#			data-Verzeichnis anlegen
	#	
	if os.path.isdir(ADDON_DATA) == False:		# Umzug durchführen
		if os.path.isdir(OLDSTORE) == True:		# nur wenn altes Verz. existiert
			msg1 = 'Das data-Verzeichnis des Addons muss umziehen.'
			msg2 = 'Der Umzug erfolgt in zwei Schritten (Backup, Umzug).'
			msg3 = '1. Schritt Backup' 
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		else:									# altes Verz. fehlt (sollte nicht vork.)
			ret = make_newDataDir()				# neues leeres Verz. anlegen
			if ret == True:						# ohne Dialog
				PLog('neues leeres Datenverzeichnis erfolgreich angelegt')
			else:
				msg1 = "Fehler: %s" % ret
				msg2 = 'Bitte Datenverzeichnis manuell kopieren / erzeugen'
				msg3 = 'oder Kontakt zum Entwickler aufnehmen'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)	
	else:
		return 'OK %s '	% ADDON_DATA			# Verz. existiert - OK
		
	#	Backkup 
	#	
	if os.path.isdir(OLDSTORE) == True:			# Test auf altes Verz. / migrieren
		try:									# 1. Backup altes Verz. 
			os.chdir(OLDPATH)					# Verz. resources
			fname 	= "data.zip"
			zipf = zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED)						
			PLog(zipf)
			getDirZipped('data', zipf)			# Verz. data in resources wird gezippt
			zipf.close()
			# 'data.zip' im 2. Arg. wird für overwrite benötigt (vorsorgl.)
			shutil.move(os.path.join(fname), os.path.join(TEMP_ADDON, 'data.zip')) 	# -> ../kodi/temp
			PLog("%s verschoben nach %s"  % (fname, TEMP_ADDON))
			ok=True
		except Exception as exception:
			ok=False
			PLog("Fehlschlag Backup: " + str(exception))
		
		if ok == True:
			msg1 = 'Backup erfolgreich - angelegt in:'
			msg2 = 	os.path.join(TEMP_ADDON, 'data.zip')
			msg3 = '2. Schritt Umzug'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		else:
			msg1 = 'Backup fehlgeschlagen - Umzug wird trotzdem  fortgesetzt.'
			msg3 = '2. Schritt Umzug'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')									
		
	#	Migration
	#	
		try:															# 2. Umzug alt -> neu
			# Backup-zip entpacken geht fixer als copytree
			shutil.copy(os.path.join(TEMP_ADDON, 'data.zip'), os.path.join(USERDATA, 'data.zip'))
			os.chdir(USERDATA)
			fname = 'data.zip'
			with zipfile.ZipFile(fname, "r") as ziphandle:
				ziphandle.extractall(USERDATA)			# entpackt in -> ../userdata/data
			os.rename(os.path.join(USERDATA, 'data'), ADDON_DATA)  # 	data -> ardundzdf_data
			os.remove('data.zip')				# wird nicht mehr gebraucht		
			ok=True							
		except Exception as exception:
			ok=False
			PLog("Entpacken data.zip fehlgeschlagen: " + str(exception))				
				
		if ok == True:
			msg1 = 'Umzug erfolgreich - neues data-Verzeichnis in:'
			msg2 = 	ADDON_DATA
			msg3 = 'Lösche altes data-Verzeichnis erst beim nächsten Update.'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			PLog(msg1); PLog(msg2);	
		else:
			msg1 = 'Umzug fehlgeschlagen'
			msg2 = 'Addon erzeugt neues leeres Datenverzeichnis'
			msg3 = 'Bitte eventuelle Fehlermeldung beachten.'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)				
			ret = make_newDataDir()					# Fallback: neues leeres Verz. anlegen
			if ret == True:
				msg1 = 'neues leeres Datenverzeichnis erfolgreich angelegt'
				msg2 = ''; msg3 = '' 
			else:
				msg1 = "Fehler: %s" % ret
				msg2 = 'Bitte Datenverzeichnis manuell kopieren / erzeugen'
				msg3 = 'oder Kontakt zum Entwickler aufnehmen'
			PLog(msg1); PLog(msg2);	
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)	
		
	return 'Ende Initialisierung'
#---------------------------
# erzeugt (einmalig) neues Datenverzeichnis (ab Version 1.4.0) 
def  make_newDataDir():
	PLog('make_newDataDir:')
	store_Dirs = ["Dict", "slides", "subtitles", "Inhaltstexte", 
				"merkliste"]
	ok=True
	for Dir in store_Dirs:
		Dir_path = os.path.join("%s/%s") % (ADDON_DATA, Dir)	
		try:  
			os.mkdir(Dir_path)
		except Exception as exception:
			ok=False
			PLog(str(exception))
			break
	if ok:
		return True
	else:
		return str(exception)
		
#---------------------------
# sichert Verz. für check_DataStores
def getDirZipped(path, zipf):
	PLog('getDirZipped:')	
	for root, dirs, files in os.walk(path):
		for file in files:
			zipf.write(os.path.join(root, file)) 
#----------------------------------------------------------------  
# Die Funktion Dict speichert + lädt Python-Objekte mittels Pickle.
#	Um uns das Handling mit keys zu ersparen, erzeugt die Funktion
#	trotz des Namens keine dicts. Aufgabe ist ein einfacher
#	persistenter Speicher. Der Name Dict lehnt sich an die
#	allerdings wesentlich komfortablere Dict-Funktion in Plex an.
#
#	Den Dict-Vorteil, dass beliebige Strings als Kennzeichnung ver-
#	wendet werden können, können wir bei Bedarf außerhalb von Dict
#	mit der vars()-Funktion ausgleichen (siehe Zuweisungen). 
#
#	Falls (außerhalb von Dict) nötig, kann mit der Zusatzfunktion 
#	name() ein Variablenname als String zurück gegeben werden.
#	
#	Um die Persistenz-Variablen von den übrigen zu unterscheiden,
#	kennzeichnen wir diese mit vorangestelltem Dict_ (ist aber
#	keine Bedingung).
#
# Zuweisungen: 
#	Dictname=value 			- z.B. Dict_sender = 'ARD-Alpha'
#	vars('Dictname')=value 	- 'Dict_name': _name ist beliebig (prg-generiert)
#	Bsp. für Speichern:
#		 Dict('store', "Dict_name", Dict_name)
#			Dateiname: 		"Dict_name"
#			Wert in:		Dict_name
#	Bsp. für Laden:
#		CurSender = Dict("load", "CurSender")
#   Bsp. für CacheTime: 5*60 (5min) - Verwendung bei "load", Prüfung mtime 
#	ev. ergänzen: OS-Verträglichkeit des Dateinamens

def Dict(mode, Dict_name='', value='', CacheTime=None):
	PLog('Dict: ' + mode)
	PLog('Dict: ' + str(Dict_name))
	PLog('Dict: ' + str(type(value)))
	dictfile = "%s/%s" % (DICTSTORE, Dict_name)
	PLog("dictfile: " + dictfile)
	
	if mode == 'store':	
		with open(dictfile, 'wb') as f: pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
		f.close
		return True
	if mode == 'remove':		# einzelne Datei löschen
		try:
			 os.remove(dictfile)
			 return True
		except:	
			return False
			
	if mode == 'ClearUp':			# Files im Dictstore älter als maxdays löschen
		maxdays = int(Dict_name)
		return ClearUp(DICTSTORE, maxdays*86400) # 1 Tag=86400 sec
			
	if mode == 'load':	
		if os.path.exists(dictfile) == False:
			PLog('Dict: %s nicht gefunden' % dictfile)
			return False
		if CacheTime:
			mtime = os.path.getmtime(dictfile)	# modified-time
			now	= time.time()
			CacheLimit = now - CacheTime		# 
			# PLog("now %d, mtime %d, CacheLimit: %d" % (now, mtime, CacheLimit))
			if CacheLimit > mtime:
				PLog('Cache miss: CacheLimit > mtime')
				return False
			else:
				PLog('Cache hit: load')	
		try:			
			with open(dictfile, 'rb')  as f: data = pickle.load(f)
			f.close
			PLog('load from Cache')
			return data
		# Exception  ausführlicher: s.o.
		except Exception as e:	
			PLog('UnpicklingError' + str(e))
			return False

#-------------------------
# Zusatzfunktion für Dict - gibt Variablennamen als String zurück
# Aufruf: name(var=var) - z.Z. nicht genutzt
def name(**variables):				
	s = [x for x in variables]
	return s[0]
#----------------------------------------------------------------
# Dateien löschen älter als seconds
#		directory 	= os.path.join(path)
#		seconds		= int (1 Tag=86400, 1 Std.=3600)
# leere Ordner werden entfernt
def ClearUp(directory, seconds):	
	PLog('ClearUp: %s, sec: %s' % (directory, seconds))	
	PLog('älter als: ' + seconds_translate(seconds))
	now = time.time()
	cnt_files=0; cnt_dirs=0
	try:
		globFiles = '%s/*' % directory
		files = glob.glob(globFiles) 
		PLog("ClearUp: globFiles " + str(len(files)))
		# PLog(" globFiles: " + str(files))
		for f in files:
			# PLog(os.stat(f).st_mtime)
			if os.stat(f).st_mtime < (now - seconds):
				os.remove(f)
				cnt_files = cnt_files + 1
			if os.path.isdir(f):		# Leerverz. entfernen
				if not os.listdir(f):
					os.rmdir(f)
					cnt_dirs = cnt_dirs + 1
		PLog("ClearUp: entfernte Dateien %s, entfernte Ordner %s" % (str(cnt_files), str(cnt_dirs)))	
		return True
	except Exception as exception:	
		PLog(str(exception))
		return False

#----------------------------------------------------------------  
# Listitems verlangen encodierte Strings auch bei Umlauten. Einige Quellen liegen in unicode 
#	vor (s. json-Auswertung in get_page) und müssen rückkonvertiert  werden.
# Hinw.: Teilstrings in unicode machen str-Strings zu unicode-Strings.
def UtfToStr(line):
	if type(line) == unicode:
		line =  line.encode('utf-8')
		return line
	else:
		return line	
#----------------------------------------------------------------  
# In Kodi fehlen die summary- und tagline-Zeilen der Plexversion. Diese ersetzen wir
#	hier einfach durch infoLabels['Plot'], wobei summary und tagline durch 
#	2 Leerzeilen getrennt werden (Anzeige links unter icon).
#
#	Sofortstart + Resumefunktion, einschl. Anzeige der Medieninfo:
#		nur problemlos, wenn das gewählte Listitem als Video (Playable) gekennzeichnet ist.
# 		mediatype steuert die Videokennz. im Listing - abhängig von Settings (Sofortstart /
#		Einzelauflösungen).
#		Mehr s. PlayVideo
#
#	Kontextmenüs (Par. cmenu): base64-Kodierung benötigt für url-Parameter (nötig für router)
#		und als Prophylaxe gegen durch doppelte utf-8-Kodierung erzeugte Sonderzeichen.
#		Dekodierung erfolgt in ShowFavs.

def addDir(li, label, action, dirID, fanart, thumb, fparams, summary='', tagline='', mediatype='', cmenu=True):
	PLog('addDir:')
	PLog('addDir - label: %s, action: %s, dirID: %s' % (label, action, dirID))
	PLog('addDir - summary: %s, tagline: %s, mediatype: %s, cmenu: %s' % (summary, tagline, mediatype, cmenu))
	
	label=UtfToStr(label); thumb=UtfToStr(thumb); fanart=UtfToStr(fanart); 
	summary=UtfToStr(summary); tagline=UtfToStr(tagline); 
	fparams=UtfToStr(fparams);

	li.setLabel(label)			# Kodi Benutzeroberfläche: Arial-basiert für arabic-Font erf.
	# PLog('summary, tagline: %s, %s' % (summary, tagline))
	Plot = ''
	if tagline:								
		Plot = tagline
	if summary:									
		Plot = "%s\n\n%s" % (Plot, summary)
		
	if mediatype == 'video': 	# "video", "music" setzen: List- statt Dir-Symbol
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot, "mediatype": "video"})	
		isFolder = False		# nicht bei direktem Player-Aufruf - OK mit setResolvedUrl
		li.setProperty('IsPlayable', 'true')					
	else:
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot})	
		li.setProperty('IsPlayable', 'false')
		isFolder = True	
	
	li.setArt({'thumb':thumb, 'icon':thumb, 'fanart':fanart})
	xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
	PLog('PLUGIN_URL: ' + PLUGIN_URL)	# plugin://plugin.video.ardundzdf/
	PLog('HANDLE: ' + str(HANDLE))
	url = PLUGIN_URL+"?action="+action+"&dirID="+dirID+"&fanart="+fanart+"&thumb="+thumb+urllib.quote_plus(fparams)
	PLog("addDir_url: " + urllib.unquote_plus(url))
		
	
	if SETTINGS.getSetting('pref_watchlist') ==  'true':	# Merkliste verwenden 
		if cmenu:											# Kontextmenüs Merkliste hinzufügen	
			Plot = Plot.replace('\n', '||')		# || Code für LF (\n scheitert in router)
			# PLog('Plot: ' + Plot)
			fparams_add = "&fparams={'action': 'add', 'name': '%s', 'thumb': '%s', 'Plot': '%s', 'url': '%s'}" \
				%   (label, thumb,  urllib.quote_plus(Plot), base64.b64encode(urllib.quote_plus(url)))
				#%   (label, thumb,  urllib.quote_plus(Plot), urllib.quote_plus(url))
				# %   (label, thumb,  base64.b64encode(url))#möglich: 'Incorrect padding' error 
			fparams_add = urllib.quote_plus(fparams_add)

			fparams_del = "&fparams={'action': 'del', 'name': '%s'}" \
				%   (label)									# name reicht für del
				# %   (label, thumb,  base64.b64encode(url))
			fparams_del = urllib.quote_plus(fparams_del)	

			li.addContextMenuItems([('Zur Merkliste hinzufügen', 'RunAddon(%s, ?action=dirList&dirID=Watch%s)' \
				% (ADDON_ID, fparams_add)), ('Aus Merkliste entfernen', 'RunAddon(%s, ?action=dirList&dirID=Watch%s)' \
				% (ADDON_ID, fparams_del))])
		else:
			pass											# Kontextmenü entfernen klappt so nicht
			#li.addContextMenuItems([('Zur Merkliste hinzufügen', 'RunAddon(%s, ?action=dirList&dirID=dummy)' \
			#	% (ADDON_ID))], replaceItems=True)

		
	xbmcplugin.addDirectoryItem(handle=HANDLE,url=url,listitem=li,isFolder=isFolder)
	
	PLog('addDir_End')		
	return	

#---------------------------------------------------------------- 
# holt kontrolliert raw-Content, cTimeout für cacheTime
# 02.09.2018	erweitert um 2. Alternative mit urllib2.Request +  ssl.SSLContext
#	Bei Bedarf get_page in EPG-Modul nachrüsten.
#	s.a. loadPage in Modul zdfmobile.
# 11.10.2018 HTTP.Request (Plex) ersetzt durch urllib2.Request
# 	03.11.2018 requests-call vorangestellt wg. Kodi-Problem: 
#	bei urllib2.Requests manchmal errno(0) (https) - Verwend. installierter Zertifikate erfolglos
# 07.11.2018 erweitert um Header-Anfrage GetOnlyRedirect zur Auswertung von Redirects (http error 302).
# Format header dict im String: "{'key': 'value'}" - Bsp. Search(), get_formitaeten()
# 23.12.2018 requests-call vorübergehend auskommentiert, da kein Python-built-in-Modul (bemerkt beim 
#	Test in Windows7
# 13.01.2019 erweitert für compressed-content (get_page2)
# 25.01.2019 Hinweis auf Redirects (get_page2)
#
def get_page(path, header='', cTimeout=None, JsonPage=False, GetOnlyRedirect=None):	
	PLog('get_page:'); PLog("path: " + path); PLog("JsonPage: " + str(JsonPage)); 
	if header:									# dict auspacken
		header = urllib2.unquote(header);  
		header = header.replace("'", "\"")		# json.loads-kompatible string-Rahmen
		header = json.loads(header)
		PLog("header: " + str(header)[:80]);
		 
	
	path = transl_umlaute(path)					# Umlaute z.B. in Podcast "Bäckerei Fleischmann"
	# path = urllib2.unquote(path)				# scheitert bei quotierten Umlauten, Ersatz replace				
	path = path.replace('https%3A//','https://')# z.B. https%3A//classic.ardmediathek.de
	msg = ''; page = ''	
	UrlopenTimeout = 10
	
	'''
	try:
		import requests															# 1. Versuch mit requests
		PLog("get_page1:")
		if GetOnlyRedirect:					# nur Redirect anfordern
			PLog('GetOnlyRedirect: ' + str(GetOnlyRedirect))
			r = requests.get(path,  stream=True, allow_redirects=True)
			page = r.url
			return page, msg					
		if header:							
			r = requests.get(path, headers=header)
		else:
			r = requests.get(path)
		PLog(r.status_code)
		page = r.text
		PLog(len(page))
		PLog(page[:100])
	except Exception as exception:
		msg = str(exception)
		msg = msg.decode(encoding="utf-8")
		PLog(msg)	
	'''
	
	if page == '':
		try:															# 2. Versuch ohne SSLContext 
			PLog("get_page2:")
			if GetOnlyRedirect:						# nur Redirect anfordern
				# Alt. hier : new_url = r.geturl()
				# bei Bedarf HttpLib2 mit follow_all_redirects=True verwenden
				PLog('GetOnlyRedirect: ' + str(GetOnlyRedirect))
				r = urllib2.urlopen(path)
				page = r.geturl()
				PLog(page)			# Url
				return page, msg					

			if header:
				req = urllib2.Request(path, headers=header)	
			else:
				req = urllib2.Request(path)										
				#req.add_header('User-Agent', 'Chrome/72.0.3626.96, Safari/537.36')
				#req.add_header('Accept', 'text/html,application/xhtml xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
				#req.add_header('Accept-Encoding','gzip, deflate, br')
			r = urllib2.urlopen(req)
			new_url = r.geturl()											# follow redirects
			PLog("new_url: " + new_url)
			# PLog("headers: " + str(r.headers))
			
			compressed = r.info().get('Content-Encoding') == 'gzip'
			PLog("compressed: " + str(compressed))
			page = r.read()
			PLog(len(page))
			if compressed:
				buf = StringIO(page)
				f = gzip.GzipFile(fileobj=buf)
				page = f.read()
				PLog(len(page))
			r.close()
			PLog(page[:100])
		except Exception as exception:
			msg = str(exception)
			msg = msg.decode(encoding="utf-8")
			PLog(msg)	

	if page == '':
		try:
			PLog("get_page3:")											# 3. Versuch mit SSLContext
			if header:
				req = urllib2.Request(path, headers=header)	
			else:
				req = urllib2.Request(path)														
			# gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
			gcontext = ssl.create_default_context()
			gcontext.check_hostname = False
			# gcontext.verify_mode = ssl.CERT_REQUIRED
			r = urllib2.urlopen(req, context=gcontext, timeout=UrlopenTimeout)
			# r = urllib2.urlopen(req)
			# PLog("headers: " + str(r.headers))
			page = r.read()
			PLog('Mark3')
			r.close()
			PLog(len(page))
		except Exception as exception:
			msg = str(exception)
			msg = msg.decode(encoding="utf-8")
			PLog(msg)						
			
	if page == '':
		error_txt = 'Seite nicht erreichbar oder nicht mehr vorhanden'			 			 	 
		msg = error_txt + ' | Seite: ' + path
		PLog(msg)
		return page, msg
		
	if JsonPage:
		PLog('json_load: ' + str(JsonPage))
		PLog(len(page))
		try:
			request = json.loads(page)
			request = json.dumps(request, sort_keys=True, indent=2, separators=(',', ': '))  # sortierte Ausgabe
			request = str(request)				# json=dict erlaubt keine Stringsuche, json.dumps klappt hier nicht
			page = request.decode('utf-8', 'ignore') # -> unicode 
			PLog("jsonpage: " + page[:100]);# PLog("msg: " + msg)		# bei Bedarf, ev. reicht nachfolg. mainVideoContent
		except Exception as exception:
			msg = str(exception)
			msg = msg.decode(encoding="utf-8")
			PLog(msg)		

	return page, msg	
#---------------------------------------------------------------- 
# img_urlScheme: img-Url ermitteln für get_sendungen, ARDRubriken. text = string, dim = Dimension
def img_urlScheme(text, dim, ID=''):
	PLog('img_urlScheme: ' + text[0:60])
	PLog(dim)
	
	pos = 	text.find('class="mediaCon">')			# img erst danach
	if pos >= 0:
		text = text[pos:]
	img_src = stringextract('img.ardmediathek.de', '##width', text)
		
	img_alt = stringextract('title="', '"', text)
	if img_alt == '':
		img_alt = stringextract('alt="', '"', text)
	img_alt = img_alt.replace('- Standbild', '')
	img_alt = 'Bild: ' + img_alt
	
		
	if img_src and img_alt:
		if img_src.startswith('http') == False:			#
			img_src = 'https://img.ardmediathek.de' + img_src 
		img_src = img_src + str(dim)					# dim getestet: 160,265,320,640
		if ID == 'PODCAST':								# Format Quadrat klappt nur bei PODCAST,
			img_src = img_src.replace('16x9', '16x16')	# Sender liefert Ersatz, falls n.v.
		if '?mandant=ard' in text:						# Anhang bei manchen Bildern
			img_src =img_src + '?mandant=ard' 
		PLog('img_urlScheme: ' + img_src)
		img_alt = UtfToStr(img_alt)
		PLog('img_urlScheme: ' + img_alt[0:40])
		return img_src, img_alt
	else:
		PLog('img_urlScheme: leer')
		return '', ''		
	
#---------------------------------------------------------------- 

# Ersetzt R-Funktion von Plex (Pfad zum Verz. Resources, hier zusätzl. Unterordner möglich) 
# Falls abs_path nicht gesetzt, wird der Pluginpfad zurückgegeben, sonst der absolute Pfad
# für lokale Icons üblicherweise PluginAbsPath.
def R(fname, abs_path=False):	
	PLog('R(fname): %s' % fname); # PLog(abs_path)
	# PLog("ADDON_PATH: " + ADDON_PATH)
	if abs_path:
		try:
			# fname = '%s/resources/%s' % (PluginAbsPath, fname)
			path = os.path.join(ADDON_PATH,fname)
			return path
		except Exception as exception:
			PLog(str(exception))
	else:
		if fname.endswith('png'):	# Icons im Unterordner images
			fname = '%s/resources/images/%s' % (ADDON_PATH, fname)
			fname = os.path.abspath(fname)
			# PLog("fname: " + fname)
			return os.path.join(fname)
		else:
			fname = "%s/resources/%s" % (ADDON_NAME, fname)
			fname = os.path.abspath(fname)
			return fname 
#----------------------------------------------------------------  
# ersetzt Resource.Load von Plex 
# abs_path s.o.	R()	
def RLoad(fname, abs_path=False): # ersetzt Resource.Load von Plex 
	if abs_path == False:
		fname = '%s/resources/%s' % (ADDON_PATH, fname)
	path = os.path.join(fname) # abs. Pfad
	PLog('RLoad: %s' % str(fname))
	try:
		with open(path,'r') as f:
			page = f.read()		
	except Exception as exception:
		PLog(str(exception))
		page = ''
	return page
#----------------------------------------------------------------
# Gegenstück zu RLoad - speichert Inhalt page in Datei fname im  
#	Dateisystem. PluginAbsPath muss in fname enthalten sein,
#	falls im Pluginverz. gespeichert werden soll   
def RSave(fname, page): 
	PLog('RSave: %s' % str(fname))
	path = os.path.join(fname) # abs. Pfad
	msg = ''					# Rückgabe leer falls OK
	try:
		with open(path,'w') as f:
			f.write(page)		
	except Exception as exception:
		msg = str(exception)
		PLog(msg)
	return msg
#----------------------------------------------------------------  
# Bsp.: #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=61000,CODECS="mp4a.40.2"
def GetAttribute(text, attribute, delimiter1 = '=', delimiter2 = ','):
	PLog('GetAttribute:')
	if attribute == 'CODECS':	# Trenner = Komma, nur bei CODEC ist Inhalt 'umrahmt' 
		delimiter1 = '="'
		delimiter2 = '"'
	x = text.find(attribute)
	if x > -1:
		y = text.find(delimiter1, x + len(attribute)) + len(delimiter1)
		z = text.find(delimiter2, y)
		if z == -1:
			z = len(text)
		return text[y:z].strip()
	else:
		return ''
#----------------------------------------------------------------  
def repl_dop(liste):	# Doppler entfernen, im Python-Script OK, Problem in Plex - s. PageControl
	mylist=liste
	myset=set(mylist)
	mylist=list(myset)
	mylist.sort()
	return mylist
#----------------------------------------------------------------  
def repl_char(cut_char, line):	# problematische Zeichen in Text entfernen, wenn replace nicht funktioniert
	line_ret = line				# return line bei Fehlschlag
	pos = line_ret.find(cut_char)
	while pos >= 0:
		line_l = line_ret[0:pos]
		line_r = line_ret[pos+len(cut_char):]
		line_ret = line_l + line_r
		pos = line_ret.find(cut_char)
		#PLog(cut_char); PLog(pos); PLog(line_l); PLog(line_r); PLog(line_ret)	# bei Bedarf	
	return line_ret
#----------------------------------------------------------------
#	doppelte utf-8-Enkodierung führt an manchen Stellen zu Sonderzeichen
#  	14.04.2019 entfernt: (':', ' ')
def repl_json_chars(line):	# für json.loads (z.B.. in router) json-Zeichen in line entfernen
	line_ret = line
	for r in	(('"', ''), ('\\', ''), ('\'', '')
		, ('&', 'und'), ('(', '<'), (')', '>'),  ('∙', '|')):			
		line_ret = line_ret.replace(*r)
	
	return line_ret
#---------------------------------------------------------------- 
# strip-Funktion, die auch Zeilenumbrüche innerhalb des Strings entfernt
#	\s [ \t\n\r\f\v - s. https://docs.python.org/3/library/re.html
def mystrip(line):	
	line_ret = line	
	line_ret = re.sub(r"\s+", " ", line)	# Alternative für strip + replace
	# PLog(line_ret)		# bei Bedarf
	return line_ret
#----------------------------------------------------------------  	
# DirectoryNavigator - Nutzung des Kodi-builtin, der Code der PMS-Version kann entfallen
# S. http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmcgui.html
# mytype: 	0 : ShowAndGetDirectory, 1 : ShowAndGetFile, 2
# mask: 	nicht brauchbar bei endungslosen Dateien, Bsp. curl
def DirectoryNavigator(settingKey, mytype, heading, shares='files', useThumbs=False, \
	treatAsFolder=False, path=''):
	PLog('DirectoryNavigator:')
	PLog(settingKey); PLog(mytype); PLog(heading); PLog(path);
	
	dialog = xbmcgui.Dialog()
	d_ret = dialog.browseSingle(int(mytype), heading, 'files', '', False, False, path)	
	PLog('d_ret: ' + d_ret)
	
	SETTINGS.setSetting(settingKey, d_ret)	
	return 
#----------------------------------------------------------------  
def stringextract(mFirstChar, mSecondChar, mString):  	# extrahiert Zeichenkette zwischen 1. + 2. Zeichenkette
	pos1 = mString.find(mFirstChar)						# return '' bei Fehlschlag
	ind = len(mFirstChar)
	#pos2 = mString.find(mSecondChar, pos1 + ind+1)		
	pos2 = mString.find(mSecondChar, pos1 + ind)		# ind+1 beginnt bei Leerstring um 1 Pos. zu weit
	rString = ''

	if pos1 >= 0 and pos2 >= 0:
		rString = mString[pos1+ind:pos2]	# extrahieren 
		
	#PLog(mString); PLog(mFirstChar); PLog(mSecondChar); 	# bei Bedarf
	#PLog(pos1); PLog(ind); PLog(pos2);  PLog(rString); 
	return rString
#---------------------------------------------------------------- 
def blockextract(blockmark, mString):  	# extrahiert Blöcke begrenzt durch blockmark aus mString
	#	blockmark bleibt Bestandteil der Rückgabe - im Unterschied zu split()
	#	Rückgabe in Liste. Letzter Block reicht bis Ende mString (undefinierte Länge),
	#		Variante mit definierter Länge siehe Plex-Plugin-TagesschauXL (extra Parameter blockendmark)
	#	Verwendung, wenn xpath nicht funktioniert (Bsp. Tabelle EPG-Daten www.dw.com/de/media-center/live-tv/s-100817)
	rlist = []				
	if 	blockmark == '' or 	mString == '':
		PLog('blockextract: blockmark or mString leer')
		return rlist
	
	pos = mString.find(blockmark)
	if 	mString.find(blockmark) == -1:
		PLog('blockextract: blockmark <%s> nicht in mString enthalten' % blockmark)
		# PLog(pos); PLog(blockmark);PLog(len(mString));PLog(len(blockmark));
		return rlist
	pos2 = 1
	while pos2 > 0:
		pos1 = mString.find(blockmark)						
		ind = len(blockmark)
		pos2 = mString.find(blockmark, pos1 + ind)		
	
		block = mString[pos1:pos2]	# extrahieren einschl.  1. blockmark
		rlist.append(block)
		# reststring bilden:
		mString = mString[pos2:]	# Rest von mString, Block entfernt	
	return rlist  
#----------------------------------------------------------------  
def teilstring(zeile, startmarker, endmarker):  		# rfind: endmarker=letzte Fundstelle, return '' bei Fehlschlag
  # die übergebenen Marker bleiben Bestandteile der Rückgabe (werden nicht abgeschnitten)
  pos2 = zeile.find(endmarker, 0)
  pos1 = zeile.rfind(startmarker, 0, pos2)
  if pos1 & pos2:
    teils = zeile[pos1:pos2+len(endmarker)]	# 
  else:
    teils = ''
  #PLog(pos1) PLog(pos2) 
  return teils 
#----------------------------------------------------------------  
def cleanhtml(line): # ersetzt alle HTML-Tags zwischen < und >  mit 1 Leerzeichen
	cleantext = line
	cleanre = re.compile('<.*?>')
	cleantext = re.sub(cleanre, ' ', line)
	return cleantext
#----------------------------------------------------------------  	
def decode_url(line):	# in URL kodierte Umlaute und & wandeln, Bsp. f%C3%BCr -> für, 	&amp; -> &
	urllib.unquote(line)
	line = line.replace('&amp;', '&')
	return line
#----------------------------------------------------------------  	
def unescape(line):
# HTML-Escapezeichen in Text entfernen, bei Bedarf erweitern. ARD auch &#039; statt richtig &#39;	
#					# s.a.  ../Framework/api/utilkit.py
#					# Ev. erforderliches Encoding vorher durchführen 
#	
	if line == None or line == '':
		return ''	
	for r in	(("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")
		, ("&#39;", "'"), ("&#039;", "'"), ("&quot;", '"'), ("&#x27;", "'")
		, ("&ouml;", "ö"), ("&auml;", "ä"), ("&uuml;", "ü"), ("&szlig;", "ß")
		, ("&Ouml;", "Ö"), ("&Auml;", "Ä"), ("&Uuml;", "Ü"), ("&apos;", "'")
		, ("&nbsp;|&nbsp;", ""), ("&nbsp;", ""),
		# Spezialfälle:
		#	https://stackoverflow.com/questions/20329896/python-2-7-character-u2013
		#	"sächsischer Genetiv", Bsp. Scott's
		#	Carriage Return (Cr)
		("–", "-"), ("&#x27;", "'"), ("&#xD;", ""), ("\xc2\xb7", "-")):
			
		line = line.replace(*r)
	return line
#----------------------------------------------------------------  
def transl_doubleUTF8(line):	# rückgängig: doppelt kodiertes UTF-8 
	# Vorkommen: Merkliste (Plot)
	# bisher nicht benötigt: ('Ã<U+009F>', 'ß'), ('ÃŸ', 'ß')
	line = UtfToStr(line)
	for r in (('Ã¤', "ä"), ('Ã„', "Ä"), ('Ã¶', "ö")		# Umlaute + ß
		, ('Ã–', "Ö"), ('Ã¼', "ü"), ('Ãœ', 'Ü')
		, ('Ã', 'ß')
		, ('\xc3\xa2', '*')):	# a mit Circumflex:  â<U+0088><U+0099> bzw. \xc3\xa2

		line = line.replace(*r)
	return line	
#----------------------------------------------------------------  
def make_filenames(title):
	# erzeugt - hoffentlich - sichere Dateinamen (ohne Extension)
	# zugeschnitten auf Titelerzeugung in meinen Plugins 
	
	title = UtfToStr(title)				# in Kodi-Version erforderlich
	fname = transl_umlaute(title)		# Umlaute
	# Ersatz: 	Leerz., Pipe, mehrf. Unterstriche -> 1 Unterstrich, Doppelp. -> Bindestrich	
	#			+ /  -> Bindestrich	
	# Entferne: Frage-, Ausrufez., Hochkomma, Komma und #@!%^&*()
	fname = (fname.replace(' ','_').replace('|','_').replace('___','_').replace('.','_')) 
	fname = (fname.replace('__','_').replace(':','-'))
	fname = (fname.replace('?','').replace('!','').replace('"','').replace('#','')
		.replace('*','').replace('@','').replace('%','').replace('^','').replace('&','')
		.replace('(','').replace(')','').replace(',','').replace('+','-').replace('/','-'))	
	
	# Die Variante .join entfällt leider, da die Titel hier bereits
	# in Unicode ankommen -	Plex code/sandbox.py:  
	# 		'str' object has no attribute '__iter__': 
	# valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
	# fname = ''.join(c for c in fname if c in valid_chars)
	return fname
#----------------------------------------------------------------  
def transl_umlaute(line):	# Umlaute übersetzen, wenn decode nicht funktioniert
	line = UtfToStr(line)				# in Kodi-Version erforderlich
	line_ret = line
	line_ret = line_ret.replace("Ä", "Ae", len(line_ret))
	line_ret = line_ret.replace("ä", "ae", len(line_ret))
	line_ret = line_ret.replace("Ü", "Ue", len(line_ret))
	line_ret = line_ret.replace('ü', 'ue', len(line_ret))
	line_ret = line_ret.replace("Ö", "Oe", len(line_ret))
	line_ret = line_ret.replace("ö", "oe", len(line_ret))
	line_ret = line_ret.replace("ß", "ss", len(line_ret))	
	return line_ret
#----------------------------------------------------------------  
def humanbytes(B):
	'Return the given bytes as a human friendly KB, MB, GB, or TB string'
	# aus https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
	B = float(B)
	KB = float(1024)
	MB = float(KB ** 2) # 1,048,576
	GB = float(KB ** 3) # 1,073,741,824
	TB = float(KB ** 4) # 1,099,511,627,776

	if B < KB:
	  return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
	elif KB <= B < MB:
	  return '{0:.2f} KB'.format(B/KB)
	elif MB <= B < GB:
	  return '{0:.2f} MB'.format(B/MB)
	elif GB <= B < TB:
	  return '{0:.2f} GB'.format(B/GB)
	elif TB <= B:
	  return '{0:.2f} TB'.format(B/TB)
#----------------------------------------------------------------  
def CalculateDuration(timecode):
	milliseconds = 0
	hours        = 0
	minutes      = 0
	seconds      = 0
	d = re.search('([0-9]{1,2}) min', timecode)
	if(None != d):
		minutes = int( d.group(1) )
	else:
		d = re.search('([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}).([0-9]{1,3})', timecode)
		if(None != d):
			hours = int ( d.group(1) )
			minutes = int ( d.group(2) )
			seconds = int ( d.group(3) )
			milliseconds = int ( d.group(4) )
	milliseconds += hours * 60 * 60 * 1000
	milliseconds += minutes * 60 * 1000
	milliseconds += seconds * 1000
	return milliseconds
#----------------------------------------------------------------  	
# Format timecode 	2018-11-28T23:00:00Z
# Rückgabe:			28.11.2018, 23:00 Uhr   (Sekunden entfallen)
def time_translate(timecode):	
	if timecode[10] == 'T' and timecode[-1] == 'Z':  # Format OK?
		year 	= timecode[:4]
		month 	= timecode[5:7]
		day 	= timecode[8:10]		
		hour 	= timecode[11:16]
		return "%s.%s.%s, %s Uhr" % (day, month, year, hour)
	else:
		return timecode
#---------------------------------------------------------------- 
# Format seconds	86400	(String, Int, Float)
# Rückgabe:  		1d, 0h, 0m, 0s	
def seconds_translate(seconds):
	if seconds == '' or seconds == 0:
		return ''
	if int(seconds) < 60:
		return "%s sec" % seconds
	seconds = float(seconds)
	day = seconds / (24 * 3600)
	time = seconds % (24 * 3600)
	hour = time / 3600
	time %= 3600
	minutes = time / 60
	time %= 60
	seconds = time
	# return "%dd, %dh, %dm, %ds" % (day,hour,minutes,seconds)
	return  "%d:%02d" % (hour, minutes)		
#---------------------------------------------------------------- 	
# Holt User-Eingabe für Suche ab
def get_keyboard_input():
	kb = xbmc.Keyboard('', 'Bitte Suchwort(e) eingeben')
	kb.doModal() # Onscreen keyboard
	if kb.isConfirmed() == False:
		return
	inp = kb.getText() # User Eingabe
	return inp	
#----------------------------------------------------------------  
# Wochentage engl./deutsch wg. Problemen mit locale-Setting 
#	für VerpasstWoche, EPG	
def transl_wtag(tag):	
	wt_engl = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	wt_deutsch = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
	
	wt_ret = tag
	for i in range (len(wt_engl)):
		el = wt_engl[i]
		if el == tag:
			wt_ret = wt_deutsch[i]
			break
	return wt_ret
#----------------------------------------------------------------  
# simpler XML-SRT-Konverter für ARD-Untertitel
#	pathname = os.path.abspath. 
#	vorh. Datei wird überschrieben
# 	Rückgabe outfile bei Erfolg, '' bei Fehlschlag
# https://knowledge.kaltura.com/troubleshooting-srt-files
# Wegen des strptime-Problems unter Kodi verzicht wir auf auf
#	korrekte Zeitübersetzung und ersetzen lediglich
#		1. den Zeitoffset 10 durch 00
#		2. das Sekundenformat 02.000 durch 02,00 (Verzicht auf die letzte Stelle)
# Problem mit dt.datetime.strptime (Kodi: attribute of type 'NoneType' is not callable):
# 	https://forum.kodi.tv/showthread.php?tid=112916
#
def xml2srt(infile):
	PLog("xml2srt: " + infile)
	outfile = '%s.srt' % infile

	with open(infile) as fin:
		text = fin.read()
		text = text.replace('-1:', '00:') 		# xml-Fehler
		# 10-Std.-Offset simpel beseitigen (2 Std. müssten reichen):
		text = (text.replace('"10:', '"00:').replace('"11:', '"01:').replace('"12:', '"02:'))
		ps = blockextract('<tt:p', text)
		
	try:
		with open(outfile, 'w') as fout:
			for i, p in enumerate(ps):
				begin 	= stringextract('begin="', '"', p)		# "10:00:07.400"
				end 	= stringextract('end="', '"', p)		# "10:00:10.920"			
				ptext	=  blockextract('tt:span style=', p)
				
				begin	= begin[:8] + ',' + begin[9:11]			# ""10:00:07,40"			
				end		= end[:8] + ',' + end[9:11]				# "10:00:10,92"

				print >>fout, i+1
				print >>fout, '%s --> %s' % (begin, end)
				# print >>fout, p.text
				for textline in ptext:
					text = stringextract('>', '<', textline) # style="S3">Willkommen zum großen</tt:span>
					print >>fout, text
				print >>fout
		os.remove(infile)									# Quelldatei entfernen
	except Exception as exception:
		PLog(str(exception))
		outfile = ''
			
	return outfile

#----------------------------------------------------------------
#	Favs / Merkliste dieses Addons einlesen
#
def ReadFavourites(mode):	
	PLog('ReadFavourites:')
	if mode == 'Favs':
		fname = xbmc.translatePath('special://profile/favourites.xml')
	else:	# 'Merk'
		fname = WATCHFILE
		
	page = RLoad(fname,abs_path=True)
			
	if mode == 'Favs':
		favs = re.findall("<favourite.*?</favourite>", page)
	else:
		favs = re.findall("<merk.*?</merk>", page)
	# PLog(favs)
	my_favs = []; fav_cnt=0;
	for fav in favs:
		if mode ==  'Favs':
			if ADDON_ID not in fav: 	# skip fremde Addons, ID's in merk's wegen 	
				continue				# 	Base64-Kodierung nicht lesbar
		my_favs.append(fav) 
		
	# PLog(my_favs)
	return my_favs

#----------------------------------------------------------------
# holt summary (Inhaltstext) für eine Sendung, abhängig von SETTINGS('pref_load_summary'). 
#	SETTINGS durch Aufrufer geprüft
#	ID: ARD, ZDF - Podcasts entspr. ARD
# Es wird nur die Webseite ausgewertet, nicht die json-Inhalte der Ladekette.
# Cache: 
#		Text wird in ../resources/data/Dict gespeichert, Dateiname aus path generiert.
#
# Aufrufer: ZDF: 	ZDF_get_content (für alle ZDF-Rubriken)
#			ARD: 	ARDStart	-> ARDStartRubrik 
#					SendungenAZ	-> ARDnew_Content
#				
#	Aufruf erfolgt, wenn für eine Sendung kein summary (teasertext, descr, ..) gefunden wird.
#
# Nicht benötigt in ARD-Suche (Search -> SinglePage -> get_sendungen): Ergebnisse 
#	enthalten einen 'teasertext' bzw. 'dachzeile'. Dto. Sendung Verpasst
# 
# Nicht benötigt in ZDF-Suche (ZDF_Search -> ZDF_get_content): Ergebnisse enthalten
#	einen verkürzten 'teaser-text'.
#
def get_summary_pre(path, ID='ZDF'):	
	PLog('get_summary_pre: ' + ID)
	
	if 'Video?bcastId' in path:					# ARDClassic
		fname = path.split('=')[-1]				# ../&documentId=31984002
		fname = "ID_%s" % fname
	else:	
		fname = path.split('/')[-1]
		fname.replace('.html', '')				# .html bei ZDF-Links abschneiden
		
	fpath = os.path.join(TEXTSTORE, fname)
	PLog('fpath: ' + fpath)
	
	summ = ''
	if os.path.exists(fpath):		# Text laden + zurückgeben
		PLog('lade lokal:') 
		summ =  RLoad(fpath, abs_path=True)
		return summ					# ev. leer, falls in der Liste eine Serie angezeigt wird 
	
	page, msg = get_page(path)
	if page == '':
		return ''
	
	if 	ID == 'ZDF':
		summ = stringextract('description" content="', '"', page)
		summ = mystrip(summ)
		#if 'title="Untertitel">UT</abbr>' in page:	# stimmt nicht mit get_formitaeten überein
		#	summ = "UT | " + summ
		
	if 	ID == 'ARDnew':
		if '/ard/player/' in path:				# json-Inhalt
			summ = stringextract('synopsis":"', '","', page)
		else:									# HTML-Inhalt
			summ = stringextract('synopsis":"', '"', page)
		summ = repl_json_chars(summ)
		
	if 	ID == 'ARDClassic':
		# summ = stringextract('description" content="', '"', page)		# geändert 23.04.2019
		summ = stringextract('itemprop="description">', '<', page)
		 	
	summ = unescape(summ)			# Text speichern
	summ = cleanhtml(summ)	
	summ = repl_json_chars(summ)
	# PLog('summ:' + summ)
	if summ:
		msg = RSave(fpath, summ)
	# PLog(msg)
	return summ
	
#---------------------------------------------------------------------------------------------------
# Icon aus livesenderTV.xml holen
# 24.01.2019 erweitert um link
# Bei Bedarf erweitern für EPG (s. SenderLiveListe)
def get_playlist_img(hrefsender):
	PLog('get_playlist_img: ' + hrefsender); 
	playlist_img=''; link='';
	playlist = RLoad(PLAYLIST)		
	playlist = blockextract('<item>', playlist)
	for p in playlist:
		s = stringextract('hrefsender>', '</hrefsender', p) 
		#s = stringextract('title>', '</title', p)	# Classic-Version
		PLog(hrefsender); PLog(s); 
		if s:									# skip Leerstrings
			if s.upper() in hrefsender.upper():
				playlist_img = stringextract('thumbnail>', '</thumbnail', p)
				playlist_img = R(playlist_img)
				link =  stringextract('link>', '</link', p)
				break
	PLog(playlist_img); PLog(link); 
	return playlist_img, link

	
####################################################################################################
# PlayVideo aktuell 23.03.2019: 
#	Sofortstart + Resumefunktion, einschl. Anzeige der Medieninfo:
#		nur problemlos, wenn das gewählte Listitem als Video (Playable) gekennzeichnet ist.
# 		mediatype steuert die Videokennz. im Listing - abhängig von Settings (Sofortstart /
#		Einzelauflösungen).
#		Dasselbe gilt für TV-Livestreams.
#		Param. Merk (added in Watch): True=Video aus Merkliste  
#
# 	Aufruf indirekt (Kennz. Playable): 	
#		ARDStartRubrik, ARDStartSingle, SinglePage (Ausnahme Podcasts),
#		SingleSendung (außer m3u8_master), SenderLiveListe, 
#		ZDF_get_content, 
#		Modul zdfMobile: PageMenu, SingleRubrik
#							
#	Aufruf direkt: 
#		ARDStartVideoStreams, ARDStartVideoMP4,
#		SingleSendung (m3u8_master), SenderLiveResolution 
#		show_formitaeten (ZDF),
#		Modul zdfMobile: ShowVideo
#
#	Format sub_path s. https://alwinesch.github.io/group__python__xbmcgui__listitem.html#ga24a6b65440083e83e67e5d0fb3379369
#	Die XML-Untertitel der ARD werden gespeichert + nach SRT konvertiert (einschl. minus 10-Std.-Offset)
#	Resume-Funktion Kodi-intern  DB MyVideos107.db, Tab files (idFile, playCount, lastPlayed) + (via key idFile),
#		bookmark (idFile, timelnSeconds, totalTimelnSeconds)
#
def PlayVideo(url, title, thumb, Plot, sub_path=None, Merk='false'):	
	PLog('PlayVideo:'); PLog(url); PLog(title);	 PLog(Plot); 
	PLog(sub_path);
	
	Plot=transl_doubleUTF8(Plot)
			
	li = xbmcgui.ListItem(path=url)		
	li.setArt({'thumb': thumb, 'icon': thumb})
	
	Plot=Plot.replace('||', '\n')				# || Code für LF (\n scheitert in router)
	# li.setProperty('IsPlayable', 'true')		# hier unwirksam
	li.setInfo(type="video", infoLabels={"Title": title, "Plot": Plot, "mediatype": "video"})
	
	# Info aus GetZDFVideoSources hierher verlagert - wurde von Kodi nach Videostart 
	#	erneut gezeigt - dto. für ARD (parseLinks_Mp4_Rtmp, ARDStartSingle)
	if sub_path:							# Vorbehandlung ARD-Untertitel
		if 'ardmediathek.de' in sub_path:	# ARD-Untertitel speichern + Endung -> .sub
			local_path = "%s/%s" % (SUBTITLESTORE, sub_path.split('/')[-1])
			local_path = os.path.abspath(local_path)
			try:
					urllib.urlretrieve(sub_path, local_path)
			except Exception as exception:
				PLog(str(exception))
				local_path = ''
			if 	local_path:
				sub_path = xml2srt(local_path)	# leer bei Fehlschlag

	PLog('sub_path: ' + str(sub_path));		
	if sub_path:							# Untertitel aktivieren, falls vorh.	
		if SETTINGS.getSetting('pref_UT_Info') == 'true':
			msg1 = 'Info: für dieses Video stehen Untertitel zur Verfügung.' 
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			
		if SETTINGS.getSetting('pref_UT_ON') == 'true':
			sub_path = 	sub_path.split('|')											
			li.setSubtitles(sub_path)
			xbmc.Player().showSubtitles(True)		
		
	# Abfrage: ist gewählter Eintrag als Video deklariert? - Falls ja,	# IsPlayable-Test
	#	erfolgt der Aufruf indirekt (setResolvedUrl). Falls nein,
	#	wird der Player direkt aufgerufen. Direkter Aufruf ohne IsPlayable-Eigenschaft 
	#	verhindert Resume-Funktion.
	# Mit xbmc.Player() ist  die Unterscheidung Kodi V18/V17 nicht mehr erforderlich,
	#	xbmc.Player().updateInfoTag bei Kodi V18 entfällt. 
	# Die Player-Varianten PlayMedia + XBMC.PlayMedia scheitern bei Kommas in Url.	
	# 
	IsPlayable = xbmc.getInfoLabel('ListItem.Property(IsPlayable)') # 'true' / 'false'
	PLog("IsPlayable: %s, Merk: %s" % (IsPlayable, Merk))
	PLog("kodi_version: " + KODI_VERSION)							# Debug
	# kodi_version = re.search('(\d+)', KODI_VERSION).group(0) # Major-Version reicht hier - entfällt
			
	#if Merk == 'true':										# entfällt bisher - erfordert
	#	xbmc.Player().play(url, li, windowed=False) 		# eigene Resumeverwaltung
	#	return
	
	if IsPlayable == 'true':								# true
		xbmcplugin.setResolvedUrl(HANDLE, True, li)			# indirekt
	else:													# false, None od. Blank
		xbmc.Player().play(url, li, windowed=False) 		# direkter Start
	return				

#---------------------------------------------------------------- 
# SSL-Probleme in Kodi mit https-Code 302 (Adresse verlagert) - Lösung:
#	 Redirect-Abfrage vor Abgabe an Kodi-Player
# Kommt vor: Kodi kann lokale Audiodatei nicht laden - Kodi-Neustart ausreichend.
# 30.12.2018  Radio-Live-Sender: bei den SSL-Links kommt der Kodi-Audio-Player auch bei der 
#	weiter geleiteten Url lediglich mit  BR, Bremen, SR, Deutschlandfunk klar. Abhilfe:
#	Wir ersetzen den https-Anteil im Link durch den http-Anteil, der auch bei tunein 
#	verwendet wird. Der Link wird bei addradio.de getrennt und mit dem http-template
#	verbunden. Der Sendername wird aus dem abgetrennten Teil ermittelt und im template
#	eingefügt.
# 	Bsp. (Sender=ndr):
#		template: 		dg-%s-http-fra-dtag-cdn.cast.addradio.de'	# %s -> sender	
#		redirect-Url: 	dg-ndr-https-dus-dtag-cdn.sslcast.addradio.de/ndr/ndr1niedersachsen/..
#		replaced-Url: 	dg-ndr-http-dus-dtag-cdn.cast.addradio.de/ndr/ndr1niedersachsen/..
# url_template gesetzt von RadioAnstalten (Radio-Live-Sender)
#
def PlayAudio(url, title, thumb, Plot, header=None, url_template=None, FavCall=''):
	PLog('PlayAudio:'); PLog(title); PLog(FavCall); 
	Plot=transl_doubleUTF8(Plot)
	
	# Weiterleitung? - Wiederherstellung https! Vorheriger Replace mit http sinnlos.
	page, msg = get_page(path=url, GetOnlyRedirect=True)
	if page:
		url = page  
		PLog('PlayAudio Redirect_Url: ' + url)

	# Kodi Header: als Referer url injiziert - z.Z nicht benötigt			
	#header='Accept-Encoding=identity;q=1, *;q=0&User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36&Accept=*/*&Referer=%s&Connection=keep-alive&Range=bytes=0-' % url
	
	if url.startswith('http') == False:		# lokale Datei
		url = os.path.abspath(url)
		
	# für Radio-Live-Sender, ersetzt https- durch http-Links. template
	#	ist für alle Radio-Live-Sender der Öffis gleich
	#	Bei Fehlschlag erhält der Player die urspr. Url 
	#	Nicht erforderlich falls Link bereits http-Link.
	if url_template and url.startswith('https'):							
		p1 = 'dg-%s-http-fra-dtag-cdn.cast.addradio.de'	# %s -> sender
		try:
			p2 = url.split('.de')[1]				# ..addradio.de/hr/youfm/live..
			s = re.search('/(.*?)/', p2).group(1)	# sender z.B. hr
			url = 'http://' + p1 %s + p2
		except Exception as exception:
			PLog(str(exception))			
		
	#if header:							
	#	Kodi Header: als Referer url injiziert - z.Z nicht benötigt	
	# 	header='Accept-Encoding=identity;q=1, *;q=0&User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36&Accept=*/*&Referer=%s&Connection=keep-alive&Range=bytes=0-' % slink	
	#	# PLog(header)
	#	url = '%s|%s' % (url, header) 
	
	PLog('PlayAudio Player_Url: ' + url)

	li = xbmcgui.ListItem(path=url)				# ListItem + Player reicht für BR
	li.setArt({'thumb': thumb, 'icon': thumb})
	ilabels = ({'Title': title})
	ilabels.update({'Comment': '%s' % Plot})	# Plot im MusicPlayer nicht verfügbar
	li.setInfo(type="music", infoLabels=ilabels)							
	li.setContentLookup(False)
	
	 	
	xbmc.Player().play(url, li, False)			# Player nicht mehr spezifizieren (0,1,2 - deprecated)

	# -> zurück zum Menü Favoriten, ohne: Rücksprung ins Bibl.-Menü
	if FavCall == 'true':
		PLog('Call_from_Favourite')
		xbmc.executebuiltin('ActivateWindow(10134)')
####################################################################################################

