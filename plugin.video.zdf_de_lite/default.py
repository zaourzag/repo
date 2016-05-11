#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import os
import re
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.zdf_de_lite'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
defaultFanart = os.path.join(addonDir ,'fanart.png')
icon = os.path.join(addonDir ,'icon.png')
addon_work_folder = xbmc.translatePath("special://profile/addon_data/"+addonID)
channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
subFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/sub.srt")
baseUrl = "http://www.zdf.de"


if not os.path.isdir(addon_work_folder):
	os.mkdir(addon_work_folder)

showSubtitles = addon.getSetting("showSubtitles") == "true"
forceViewMode = addon.getSetting("forceView") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewIDVideos"))
viewModeShows = str(addon.getSetting("viewIDShows"))
minLength = addon.getSetting("minLengthNew")
mins = [0, 5, 10, 20, 30]
minLength = mins[int(minLength)]
videoQuality = int(addon.getSetting("videoQuality"))
zdfMetaEnabled = addon.getSetting("zdfMetaEnabled") == "true"
expertEnabled = addon.getSetting("expertEnabled") == "true"
forceHttp = addon.getSetting("forceHttp") == "true" and expertEnabled and zdfMetaEnabled#konvertiert rtmp streams zu http streams. siehe http://wiki.ubuntuusers.de/Baustelle/Streams_speichern/Beispiele#Die-Mediatheken-von-ZDF-und-3sat
rtspEnabled = addon.getSetting("rtspEnabled") == "true" and expertEnabled
threegpEnabled = addon.getSetting("threegpEnabled") == "true" and expertEnabled
wmv3Enabled = addon.getSetting("wmv3Enabled") == "true" and expertEnabled
httpEnabled = addon.getSetting("httpEnabled") == "true" and expertEnabled or not expertEnabled
preferHttp = addon.getSetting("preferHttp") == "true"

def index():
	#addDir(translation(30010), "", 'listShowsFavs', "")
	#addDir(translation(30030), "", 'listChannels', "")
	addDir(translation(30006), baseUrl+"/ZDFmediathek/hauptnavigation/startseite/aktuellste", 'listVideos', "")
	#addDir(translation(30005), baseUrl+"/ZDFmediathek/hauptnavigation/startseite/tipps", 'listVideos', "")
	addDir(translation(30007), baseUrl+"/ZDFmediathek/hauptnavigation/startseite/meist-gesehen", 'listVideos', "")
	addDir(translation(30001), "", 'listAZ', "")
	addDir(translation(30013), baseUrl+"/ZDFmediathek/hauptnavigation/sendung-verpasst", 'listVerpasst', "")
	addDir(translation(30003), baseUrl+"/ZDFmediathek/hauptnavigation/nachrichten/ganze-sendungen", 'listShows', "")
	addDir(translation(30031), "", 'listColumns', "")
	addDir(translation(30004), baseUrl+"/ZDFmediathek/hauptnavigation/themen", 'listThemen', "")
	addDir(translation(30002), "", 'search', "")
	addDir("LiveTV", baseUrl+"/ZDFmediathek/hauptnavigation/live/day0", 'listVideos', "")
	xbmcplugin.endOfDirectory(pluginhandle)


def listChannels():
	addDir("ZDF", "zdf", 'listChannel', baseUrl+"/ZDFmediathek/contentblob/1209114/tImg/4009328")
	addDir("ZDFneo", "zdfneo", 'listChannel', baseUrl+"/ZDFmediathek/contentblob/1209122/tImg/5939058")
	addDir("ZDFkultur", "zdfkultur", 'listChannel', baseUrl+"/ZDFmediathek/contentblob/1317640/tImg/5960283")
	addDir("ZDFinfo", "zdfinfo", 'listChannel', baseUrl+"/ZDFmediathek/contentblob/1209120/tImg/5880352")
	addDir("3sat", "dreisat", 'listChannel', baseUrl+"/ZDFmediathek/contentblob/1209116/tImg/5784929")
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def listColumns():
	addDir("Filme", baseUrl+"/ZDFmediathek/kanaluebersicht/aktuellste/1829656", 'listVideos', "")
	addDir("Serien", baseUrl+"/ZDFmediathek/kanaluebersicht/aktuellste/1859968", 'listVideos', "")
	addDir("Dokus", baseUrl+"/ZDFmediathek/kanaluebersicht/aktuellste/180", 'listVideos', "")
	addDir("HD", baseUrl+"/ZDFmediathek/suche?sucheText=hd", 'listVideos', "")
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVerpasst(url):
	content = getUrl(url)
	content = content[content.find('<ul class="subNavi">'):]
	content = content[:content.find('</ul>')]
	match = re.compile('<a href="(.+?)"[^>]*>(.+?)</a>', re.DOTALL).findall(content)
	for url, title in match:
		addDir(title[2:], baseUrl+url, 'listVideos', "")
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsFavs():
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	if os.path.exists(channelFavsFile):
		fh = open(channelFavsFile, 'r')
		all_lines = fh.readlines()
		for line in all_lines:
			title = line[line.find("###TITLE###=")+12:]
			title = title[:title.find("#")]
			url = line[line.find("###URL###=")+10:]
			url = url[:url.find("#")]
			thumb = line[line.find("###THUMB###=")+12:]
			thumb = thumb[:thumb.find("#")]
			if title=="heute - 100sec":
				addShowFavLink(title, "", 'play100sec', thumb)
			else:
				addShowFavDir(title, urllib.unquote_plus(url), "listVideos", thumb)
		fh.close()
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def listChannel(url):
	if url == "zdf":
		addDir(translation(30006), baseUrl+"/ZDFmediathek/senderstartseite/sst1/1209114", 'listVideos', "")
		addDir(translation(30007), baseUrl+"/ZDFmediathek/senderstartseite/sst2/1209114", 'listVideos', "")
	elif url == "zdfneo":
		addDir(translation(30006), baseUrl+"/ZDFmediathek/kanaluebersicht/aktuellste/857392", 'listVideos', "")
		addDir(translation(30005), baseUrl+"/ZDFmediathek/senderstartseite/sst0/1209122", 'listVideos', "")
		addDir(translation(30008), baseUrl+"/ZDFmediathek/senderstartseite/sst1/1209122", 'listShows', "")
		addDir(translation(30007), baseUrl+"/ZDFmediathek/senderstartseite/sst2/1209122", 'listVideos', "")
	elif url == "zdfkultur":
		addDir(translation(30006), baseUrl+"/ZDFmediathek/kanaluebersicht/aktuellste/1321386", 'listVideos', "")
		addDir(translation(30005), baseUrl+"/ZDFmediathek/senderstartseite/sst0/1317640", 'listVideos', "")
		addDir(translation(30008), baseUrl+"/ZDFmediathek/senderstartseite/sst1/1317640", 'listShows', "")
		addDir(translation(30007), baseUrl+"/ZDFmediathek/senderstartseite/sst2/1317640", 'listVideos', "")
	elif url == "zdfinfo":
		addDir(translation(30006), baseUrl+"/ZDFmediathek/kanaluebersicht/aktuellste/398", 'listVideos', "")
		addDir(translation(30005), baseUrl+"/ZDFmediathek/senderstartseite/sst0/1209120", 'listVideos', "")
		addDir(translation(30008), baseUrl+"/ZDFmediathek/senderstartseite/sst1/1209120", 'listShows', "")
		addDir(translation(30007), baseUrl+"/ZDFmediathek/senderstartseite/sst2/1209120", 'listVideos', "")
	elif url == "dreisat":
		addDir(translation(30006), baseUrl+"/ZDFmediathek/senderstartseite/sst1/1209116", 'listVideos', "")
		addDir(translation(30008), baseUrl+"/ZDFmediathek/senderstartseite/sst2/1209116", 'listShows', "")
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows(url, bigThumb):
	if "/nachrichten/ganze-sendungen" in url:
		addShowLink("heute - 100sec", "", 'play100sec', baseUrl+"/ZDFmediathek/contentblob/257404/timg485x273blob/8232227")
	content = getUrl(url)
	spl = content.split('<div class="image">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		match = re.compile('<a href="(.+?)">', re.DOTALL).findall(entry)
		url = match[0]
		match = re.compile('<img src="(.+?)"', re.DOTALL).findall(entry)
		thumb = match[0]
		if bigThumb == True:
			thumb = thumb.replace("/timg94x65blob", "/timg485x273blob")
		else:
			thumb = thumb.replace('timg94x65blob','timg173x120blob')
		match = re.compile('<p><b><a href="(.+?)">(.+?)<br />', re.DOTALL).findall(entry)
		title = match[0][1]
		title = cleanTitle(title)
		if "?bc=nrt;nrg&amp;gs=446" not in url and "?bc=nrt;nrg&amp;gs=1456548" not in url and "?bc=nrt;nrg&amp;gs=1384544" not in url and "?bc=nrt;nrg&amp;gs=1650526" not in url and "?bc=nrt;nrg&amp;gs=1650818" not in url:
			if bigThumb:
				addShowDir(title, baseUrl+url, 'listVideos', baseUrl+thumb)
			else:
				addTopicDir(title, baseUrl+url, 'listVideos', baseUrl+thumb)
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def listVideos(url):
	urlMain = url
	if "/nachrichten/ganze-sendungen" in url:
		url = url.replace("&amp;", "&")+"&teaserListIndex=75"
	elif "/hauptnavigation/startseite/" in url:
		pass
	else:
		if "?bc=" in url:
			url = url[:url.find("?bc=")]
		if "?sucheText=" not in url:
			url = url+"?teaserListIndex=975"
	content = getUrl(url)
	spl = content.split('<div class="image">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		if "BILDER</a></p>" not in entry and ">INTERAKTIV</a></p>" not in entry and "BEITR&Auml;GE" not in entry:
			match1 = re.compile('/video/(.+?)/', re.DOTALL).findall(entry)
			match2 = re.compile('/live/(.+?)/', re.DOTALL).findall(entry)
			if match1:
				url = match1[0]
			elif match2:
				url = match2[0]
			match = re.compile('<p class="grey"><a href="(.+?)">(.+?)</a></p>', re.DOTALL).findall(entry)
			date = ""
			if match:
				date = match[0][1]
			date = date.replace('<span class="orange">', '').replace('</span>', '')
			date = cleanTitle(date)
			match = re.compile('>VIDEO, (.+?)<', re.DOTALL).findall(entry)
			length = ""
			if match:
				length = match[0]
				if length.startswith("00:"):
					length = "1"
			match = re.compile('<img src="(.+?)"', re.DOTALL).findall(entry)
			thumb = match[0]
			thumb = thumb.replace("/timg94x65blob", "/timg485x273blob")
			if baseUrl not in thumb:
				thumb = baseUrl+thumb
			match = re.compile('<p><b><a href="(.+?)">(.+?)<br />', re.DOTALL).findall(entry)
			title = match[0][1]
			title = cleanTitle(title)
			if "/hauptnavigation/sendung-verpasst/" in urlMain:
				date = date[date.rfind(" "):]
			else:
				if ".20" in date:
					date = date[:date.find(".20")]
			if "," in date:
				title = date.split(",")[1].strip()+" - "+date.split(",")[0].strip()+": "+title
			if "/live/day0" in urlMain and ">LIVE</a></p>" in entry:
				addLink(title.replace("live-bis 00:00, ", ""), url, 'playVideo', thumb, length)
			elif urlMain.find("/live/day0") == -1 and entry.find(">LIVE</a></p>") == -1:
				minutes = 999
				if ":" in length:
					minutes = int(length[:length.find(":")])
				elif " " in length:
					minutes = int(length[:length.find(" ")])
				if minutes >= minLength:
					addLink(title, url, 'playVideo', thumb, length)
	content = content[content.find('<span class="paging">'):]
	match = re.compile('<a href="/ZDFmediathek/suche(.+?)" class="forward">(.+?)</a>', re.DOTALL).findall(content)
	for url, title in match:
		if title == "Weiter":
			addDir(translation(30011), baseUrl+"/ZDFmediathek/suche"+url.replace("&amp;", "&"), 'listVideos', "")
	xbmcplugin.endOfDirectory(pluginhandle)
	if "/live/day0" in urlMain:
		vm = viewModeShows
	else:
		vm = viewMode
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+vm+')')


def play100sec():
	content = getUrl(baseUrl+"/ZDFmediathek/100sec")
	match = re.compile('assetID : (.+?),', re.DOTALL).findall(content)
	playVideo(match[0])


def playVideo(id):
	baseVideoUrl = "http://nrodl.zdf.de/de"
	content = getUrl(baseUrl+"/ZDFmediathek/xmlservice/web/beitragsDetails?id="+id)
	#print content
	match = re.compile('<formitaet basetype="(.+?)" isDownload=".+?">(.+?)</formitaet>', re.DOTALL).findall(content)
	subtitleUrl = False
	if '<caption>' in content:
		try:
			caption = re.compile('<caption>(.+?)</caption>', re.DOTALL).findall(content)[0]
			subtitleUrl = re.compile('<url>(.+?)</url>', re.DOTALL).findall(caption)[0]
			if '<offset>' in caption:
				offset = int(re.compile('<offset>(.+?)</offset>', re.DOTALL).findall(caption)[0])
			else:
				offset = 0
		except: pass
	if '<default-stream-url>' in content:
		url = re.compile('<default-stream-url>(.+?)</default-stream-url>', re.DOTALL).findall(content)[0]
	elif '<type>livevideo</type>' in content:
		url = re.compile('<formitaet basetype="h264_aac_ts_http_m3u8_http" isDownload="false">.+?<quality>high</quality>.+?<url>(.+?)</url>', re.DOTALL).findall(content)[0]
	else:
		lastBr = 0
		for basetype,entry in match:
			#print basetype
			possibleUrl = False
			facet = re.compile('<facet>(.+?)</facet>', re.DOTALL).findall(entry)
			if not facet or facet[0] != 'podcast':
				videoUrl = re.compile('<url>(.+?)</url>', re.DOTALL).findall(entry)[0]
				#print videoUrl
				quality = re.compile('<quality>(.+?)</quality>', re.DOTALL).findall(entry)[0]
				videoBitrate = int(re.compile('<videoBitrate>(.+?)</videoBitrate>', re.DOTALL).findall(entry)[0])
				if   basetype == 'h264_aac_mp4_rtsp_mov_http'     and rtspEnabled:
					possibleUrl, possibleBr = _chooseVideo(videoUrl,videoBitrate,lastBr,facet)
				elif basetype == 'h264_aac_3gp_http_na_na'        and threegpEnabled:
					possibleUrl, possibleBr = _chooseVideo(videoUrl,videoBitrate,lastBr,facet)
				elif basetype == 'wmv3_wma9_asf_mms_asx_http'     and wmv3Enabled:
					possibleUrl, possibleBr = _chooseVideo(videoUrl,videoBitrate,lastBr,facet)
				elif basetype == 'h264_aac_mp4_rtmp_zdfmeta_http' and zdfMetaEnabled:
					possibleUrl, possibleBr = _chooseVideo(videoUrl,videoBitrate,lastBr,facet)
				elif basetype == 'h264_aac_mp4_http_na_na'        and httpEnabled:
					possibleUrl, possibleBr = _chooseVideo(videoUrl,videoBitrate,lastBr,facet) 
					if forceHttp:
						if not facet or facet[0] != 'hbbtv':
							baseVideoUrl = videoUrl.split('/zdf/')[0]#die basis ist nicht immer gleich

				if possibleUrl:
					if possibleBr > lastBr or basetype == 'h264_aac_mp4_http_na_na' and preferHttp and possibleBr == lastBr:
						url = possibleUrl
						lastBr = possibleBr

	if url.endswith('.meta'):
		meta = getUrl(url)
		url = re.compile('<default-stream-url>(.+?)</default-stream-url>', re.DOTALL).findall(meta)[0]
		if forceHttp and 'mp4:' in url:
			url = baseVideoUrl+'/'+url.split('mp4:')[-1]

	listitem = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	if showSubtitles and subtitleUrl:
		setSubtitle(subtitleUrl,offset)

def _chooseVideo(videoUrl,videoBitrate,lastBr,facet):
	url = False
	if lastBr == 0:
		url = videoUrl
		lastBr = videoBitrate
	elif videoQuality == 0:#low
		if videoBitrate <= 1300000:
			if not facet or facet[0] != 'hbbtv':
				url = videoUrl
				lastBr = videoBitrate
	elif videoQuality == 1:#medium
		if int(videoBitrate) <= 1500000:
			if not facet or facet[0] != 'hbbtv':
				url = videoUrl
				lastBr = videoBitrate
	elif videoQuality == 2:#high 25p
		if not facet or facet[0] != 'hbbtv':
			if '1456k_p13v11.mp4' in videoUrl:
				url = videoUrl.replace('1456k_p13v11.mp4','2256k_p14v11.mp4')
				lastBr = 2200000
			else:
				url = videoUrl
				lastBr = videoBitrate
	elif videoQuality == 3:#high 50i
		if not facet or facet[0] != 'hbbtv':
			if '1456k_p13v11.mp4' in videoUrl:
				url = videoUrl.replace('1456k_p13v11.mp4','2328k_p35v11.mp4')
				lastBr = 2200000
			else:
				url = videoUrl
				lastBr = videoBitrate
	return url,lastBr
def setSubtitle(url,offset=0):
	if os.path.exists(subFile):
		os.remove(subFile)
	try:
		content = getUrl(url)
	except:
		content = ""
	if content:
		matchLine = re.compile('<p begin="(.+?)" end="(.+?)"(.+?)>(.+?)</p>', re.DOTALL).findall(content)
		fh = open(subFile, 'a')
		count = 1
		for begin, end, info, line in matchLine:
			color = False
			begin = float(begin) - offset
			beginS = str(round(begin%60, 1)).replace(".",",")
			if len(beginS.split(",")[0])==1:
				beginS = "0"+beginS
			beginM = str((int(begin)/60)%60)
			if len(beginM)==1:
				beginM = "0"+beginM
			beginH = str(int(begin)/60/60)
			if len(beginH)==1:
				beginH = "0"+beginH
			begin = beginH+":"+beginM+":"+beginS
			end = float(end) - offset
			endS = str(round(end%60, 1)).replace(".",",")
			if len(endS.split(",")[0])==1:
				endS = "0"+endS
			endM = str((int(end)/60)%60)
			if len(endM)==1:
				endM = "0"+endM
			endH = str(int(end)/60/60)
			if len(endH)==1:
				endH = "0"+endH
			end = endH+":"+endM+":"+endS
			match = re.compile('<span(.+?)>', re.DOTALL).findall(line)
			for span in match:
				line = line.replace("<span"+span+">","")
			if 'tts:color' in info:
				color = re.compile('tts:color="(.+?)"').findall(info)[0]
				line = '<font color="'+color+'">'+line.strip()+'</font>'
			line = line.replace("<br />","\n").replace("</span>","").strip()
			fh.write(str(count)+"\n"+begin+" --> "+end+"\n"+cleanTitle(line)+"\n\n")
			count+=1
		fh.close()
		xbmc.sleep(1000)
		xbmc.Player().setSubtitles(subFile)

"""
def setSubtitle(url,offset=0):
	if os.path.exists(subFile):
		os.remove(subFile)
	try:
		content = getUrl(url)
	except:
		content = ""
	if content:
		matchLine = re.compile('<p begin="(.+?)" end="(.+?)"(.+?)>(.+?)</p>', re.DOTALL).findall(content)
		fh = open(subFile, 'a')
		count = 1
		for begin, end, info, line in matchLine:
			color = False
			begin = float(begin)
			beginS = str(round(begin%60, 1)).replace(".",",")
			if len(beginS.split(",")[0])==1:
				beginS = "0"+beginS
			beginM = str((int(begin)/60)%60)
			if len(beginM)==1:
				beginM = "0"+beginM
			beginH = str(int(begin)/60/60)
			if len(beginH)==1:
				beginH = "0"+beginH
			begin = beginH+":"+beginM+":"+beginS
			end = float(end)
			endS = str(round(end%60, 1)).replace(".",",")
			if len(endS.split(",")[0])==1:
				endS = "0"+endS
			endM = str((int(end)/60)%60)
			if len(endM)==1:
				endM = "0"+endM
			endH = str(int(end)/60/60)
			if len(endH)==1:
				endH = "0"+endH
			end = endH+":"+endM+":"+endS
			match = re.compile('<span(.+?)>', re.DOTALL).findall(line)
			for span in match:
				line = line.replace("<span"+span+">","")
			if 'tts:color' in info:
				color = re.compile('tts:color="(.+?)"').findall(info)[0]
				line = '<font color="'+color+'">'+line+'</font>'
			line = line.replace("<br />","\n").replace("</span>","").strip()
			fh.write(str(count)+"\n"+begin+" --> "+end+"\n"+cleanTitle(line)+"\n\n")
			count+=1
		fh.close()
		xbmc.sleep(1000)
		xbmc.Player().setSubtitles(subFile)
"""

def queueVideo(url, name):
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	listitem = xbmcgui.ListItem(name)
	playlist.add(url, listitem)


def search():
	keyboard = xbmc.Keyboard('', translation(30002))
	keyboard.doModal()
	if keyboard.isConfirmed() and keyboard.getText():
		search_string = keyboard.getText().replace(" ", "+")
		listVideos(baseUrl+"/ZDFmediathek/suche?sucheText="+search_string)


def listAZ():
	addDir("ABC", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz0", 'listShows', "")
	addDir("DEF", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz1", 'listShows', "")
	addDir("GHI", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz2", 'listShows', "")
	addDir("JKL", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz3", 'listShows', "")
	addDir("MNO", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz4", 'listShows', "")
	addDir("PQRS", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz5", 'listShows', "")
	addDir("TUV", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz6", 'listShows', "")
	addDir("WXYZ", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz7", 'listShows', "")
	addDir("0-9", baseUrl+"/ZDFmediathek/hauptnavigation/sendung-a-bis-z/saz8", 'listShows', "")
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def cleanTitle(title):
	title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
	title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace("&eacute;", "é").replace("&egrave;", "è")
	title = title.replace("&#x00c4","Ä").replace("&#x00e4","ä").replace("&#x00d6","Ö").replace("&#x00f6","ö").replace("&#x00dc","Ü").replace("&#x00fc","ü").replace("&#x00df","ß").strip()
	title = title.replace("&apos;","'").strip()
	return title


def favs(param):
	mode = param[param.find("###MODE###=")+11:]
	mode = mode[:mode.find("###")]
	channelEntry = param[param.find("###TITLE###="):]
	if mode == "ADD":
		if os.path.exists(channelFavsFile):
			fh = open(channelFavsFile, 'r')
			content = fh.read()
			fh.close()
			if content.find(channelEntry) == -1:
				fh = open(channelFavsFile, 'a')
				fh.write(channelEntry+"\n")
				fh.close()
		else:
			fh = open(channelFavsFile, 'a')
			fh.write(channelEntry+"\n")
			fh.close()
	elif mode == "REMOVE":
		refresh = param[param.find("###REFRESH###=")+14:]
		refresh = refresh[:refresh.find("#")]
		fh = open(channelFavsFile, 'r')
		content = fh.read()
		fh.close()
		entry = content[content.find(channelEntry):]
		fh = open(channelFavsFile, 'w')
		fh.write(content.replace(channelEntry+"\n", ""))
		fh.close()
		if refresh == "TRUE":
			xbmc.executebuiltin("Container.Refresh")


def getUrl(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	return link

def cleanDuration(duration):
	try:
		if ':' in duration:
			s = duration.split(':')[0]
			if int(s[1]) >= 30:
				duration = str(int(s[0])+1)
			else:
				duration = s[0]
		else:
			duration = duration.replace(' min','')
	except:
		pass
	return duration

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict


def addLink(name, url, mode, iconimage, duration=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	duration = cleanDuration(duration)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration})
	liz.setProperty('IsPlayable', 'true')
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultFanart)
	liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok


def addShowLink(name, url, mode, iconimage, duration=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	duration = cleanDuration(duration)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration})
	liz.setProperty('IsPlayable', 'true')
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultFanart)
	playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
	liz.addContextMenuItems([(translation(30028), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok


def addShowFavLink(name, url, mode, iconimage, duration=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	duration = cleanDuration(duration)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration})
	liz.setProperty('IsPlayable', 'true')
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultFanart)
	playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
	liz.addContextMenuItems([(translation(30029), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok


def addDir(name, url, mode, iconimage):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultFanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addTopicDir(name, url, mode, iconimage):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultFanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addShowDir(name, url, mode, iconimage):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultFanart)
	playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
	liz.addContextMenuItems([(translation(30028), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addShowFavDir(name, url, mode, iconimage):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultFanart)
	playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
	liz.addContextMenuItems([(translation(30029), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'listChannel':
	listChannel(url)
elif mode == 'listVideos':
	listVideos(url)
elif mode == 'listShows':
	listShows(url, True)
elif mode == 'listThemen':
	listShows(url, False)
elif mode == 'listVerpasst':
	listVerpasst(url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'play100sec':
	play100sec()
elif mode == 'listChannels':
	listChannels()
elif mode == 'listColumns':
	listColumns()
elif mode == 'queueVideo':
	queueVideo(url, name)
elif mode == 'search':
	search()
elif mode == 'listAZ':
	listAZ()
elif mode == 'favs':
	favs(url)
elif mode == 'listShowsFavs':
	listShowsFavs()
else:
	index()
