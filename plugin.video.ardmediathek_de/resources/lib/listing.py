#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import xbmcplugin
import xbmcgui
import urllib
import utils
useThumbAsFanart = True
baseUrl = "http://www.ardmediathek.de"
defaultThumb = baseUrl+"/ard/static/pics/default/16_9/default_webM_16_9.jpg"
defaultBackground = "http://www.ard.de/pool/img/ard/background/base_xl.jpg"
icon = ''#todo

def getAllAZ(letter):
	items = []
	l = getAZ(letter)
	for name, url, thumb in l:
		#u = sys.argv[0]+"?url="+urllib.quote_plus(baseUrl+url+'&m23644322=quelle.tv&rss=true')+"&name="+urllib.quote_plus(name)+"&mode=listVideosRss"+"&nextpage=True"+"&hideshowname=True"+"&showName="+urllib.quote_plus(name)
		u = sys.argv[0]+"?url="+urllib.quote_plus(baseUrl+url+'&m23644322=quelle.tv&rss=true')+"&name="+urllib.quote_plus(name)+"&mode=listVideosRss"+"&nextpage=True"+"&hideshowname=True"+"&showName="+urllib.quote_plus(name)
		liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=thumb)
		liz.setInfo(type="Video", infoLabels={"Title": name})
		if useThumbAsFanart:
			if not thumb or thumb==icon or thumb==defaultThumb:
				thumb = defaultBackground
			liz.setProperty("fanart_image", thumb)
		else:
			liz.setProperty("fanart_image", defaultBackground)
		items.append([u, liz, True])
	return items
		

def getAZ(letter):
	if letter == '#':
		letter = '0-9'
	list = []
	content = utils.getUrl(baseUrl+"/tv/sendungen-a-z?buchstabe="+letter)
	spl = content.split('<div class="teaser" data-ctrl')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
		url = match[0].replace("&amp;","&")
		match = re.compile('class="headline">(.+?)<', re.DOTALL).findall(entry)
		title = match[0]
		match = re.compile('/image/(.+?)/16x9/', re.DOTALL).findall(entry)
		thumb = baseUrl+"/image/"+match[0]+"/16x9/0"
		list.append([title, url, thumb])
	return list
	
def getVideosXml(videoId):
	list = []
	content = utils.getUrl(baseUrl+'/ard/servlet/export/collection/collectionId='+videoId+'/index.xml')
	match = re.compile('<content>(.+?)</content>', re.DOTALL).findall(content)
	for item in match:
		clip = re.compile('<clip(.+?)>', re.DOTALL).findall(item)[0]
		if 'isAudio="false"' in clip:
			name = re.compile('<name>(.+?)</name>', re.DOTALL).findall(item)[0]
			length = re.compile('<length>(.+?)</length>', re.DOTALL).findall(item)[0]
			if not '<mediadata:images/>' in item:
				thumb = re.compile('<image.+?url="(.+?)"', re.DOTALL).findall(item)[-1]
			else:
				thumb = ''
			id = re.compile(' id="(.+?)"', re.DOTALL).findall(clip)[0]
			list.append([name, id, thumb, length])
	return list