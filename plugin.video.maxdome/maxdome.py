#!/usr/bin/env python
# coding: utf8

import sys
import os
import requests
import json
import pickle
import re
import HTMLParser
from BeautifulSoup import BeautifulSoup
import xbmcaddon

addon = xbmcaddon.Addon()

class MaxdomeSession:
	def __init__(self, username, password, pathToCookies):
		self.Assets = MaxdomeAssets(self)
		self.session = requests.Session()
		self.cookie_path = pathToCookies
		self.username = username
		self.password = password
		self.customer_id = ''
		self.session.headers.setdefault('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')
		
		#Maxdome URLs
		self.baseurl = 'https://www.maxdome.de'
		self.api_url = 'https://heimdall.maxdome.de'
		self.login_url = 'https://www.maxdome.de/_ajax/process/login/start/login0'
		self.order_url = 'https://www.maxdome.de/_ajax/process/videoOrder/start/orderMovie0'
		self.play_url = 'http://play.maxdome.de/webplayer'
		self.license_url = ''
		self.video_url = ''
		
		#Load cookies from last session if available
		if os.path.isfile(self.cookie_path):
			with open(self.cookie_path) as f:
				cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
				self.session.cookies = cookies
				
		if not self.isLoggedIn():
			self.session.cookies.clear_session_cookies()
			if self.login():
				self.session.cookies['quality'] = self.getPreferences()['orderQuality']
				self.session.cookies['mxd-ua'] = '%7B%22os%22%3A%7B%22name%22%3A%22Linux%22%2C%22version%22%3A%22x86_64%22%7D%2C%22browser%22%3A%7B%22name%22%3A%22Chrome%22%2C%22version%22%3A%2248.0.2564.116%22%2C%22major%22%3A%2248%22%2C%22architecture%22%3A%2232%22%7D%7D'
				with open(self.cookie_path, 'w') as f:
					pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

	def isLoggedIn(self):
		r = self.session.get(self.baseurl + '/mein-account')
		strKey = 'isLoggedIn: '
		startpos = r.text.find(strKey) + len(strKey)
		endpos = r.text.find(',', startpos)
		value = r.text[startpos:endpos]
		if 'true' in value:
			self.customer_id = self.getCustomerId(r.text)
			return True

		return False

	def getCustomerId(self, text):
		strKey = 'Maxdome.customerId = \''
		startpos = text.find(strKey) + len(strKey)
		endpos = text.find('\';', startpos)
		return text[startpos:endpos]

	def getPreferences(self):
		headers = {'accept':'application/vnd.maxdome.im.v8+json', 'Accept-Encoding':'gzip, deflate, sdch', 'Accept-Language':'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4', 'client':'mxd_package', 'clienttype': 'webportal', 'Connection': 'keep-alive', 'content-type':'application/json', 'customerId':self.customer_id, 'language':'de_DE', 'Maxdome-Origin':'maxdome.de', 'mxd-session':self.session.cookies['mxd-bbe-session'], 'platform':'web'}
		r = self.session.get(self.api_url + '/interfacemanager-2.1/mxd/customer/' + self.customer_id + '/preference', headers=headers)
		
		return r.json()

	def login(self):	
		headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'Accept-Language':'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4', 'connection': 'keep-alive', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://www.maxdome.de', 'Referer': 'https://www.maxdome.de/'}
		payload = {'userId': self.username, 'phrase': self.password, 'autoLogin': 'true'}

		r = self.session.post(self.login_url, headers=headers, data=payload)
		if 'Erfolgreich angemeldet' in r.text:
			#Save cookies
#			self.session.cookies['quality'] = self.getPreferences()['orderQuality']
#			self.session.cookies['mxd-ua'] = '%7B%22os%22%3A%7B%22name%22%3A%22Linux%22%2C%22version%22%3A%22x86_64%22%7D%2C%22browser%22%3A%7B%22name%22%3A%22Chrome%22%2C%22version%22%3A%2248.0.2564.116%22%2C%22major%22%3A%2248%22%2C%22architecture%22%3A%2232%22%7D%7D'
#			with open(self.cookie_path, 'w') as f:
#				pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

			return self.isLoggedIn()

		return False

	def play(self, assetId):
		headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'Accept-Language':'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4', 'connection': 'keep-alive', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://www.maxdome.de', 'Referer': 'https://www.maxdome.de/ab-durch-die-hecke-2152374.html', 'Host': 'www.maxdome.de'}
		payload = {'assetId': assetId, 'licenseType': 'auto', 'isPreorder': 0, 'isHd': 1, 'orderableSeasonId': 0, 'portalHost': 'https://www.maxdome.de', 'ignoreResumeTime': 0}

		r = self.session.post(self.order_url, headers=headers, data=payload, allow_redirects=True)
		if r.status_code != 200:
			return False

		url = self.play_url + '/' + str(assetId)
		r = self.session.get(url, headers=headers, allow_redirects=False)
		startpos = r.text.find('dash:') + 6
		endpos = r.text.find('},', startpos) + 1
		data = json.loads(r.text[startpos:endpos])
		self.license_url = data['licenseUrl'] + '|User-Agent=Mozilla%2F5.0%20(X11%3B%20Linux%20x86_64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F49.0.2623.87%20Safari%2F537.36&Referer=http%3A%2F%2Fplay.maxdome.de%2Fwebplayer%2Fhttps%253A%252F%252Fwww.maxdome.de%252Fab-durch-die-hecke-2152374.html?portal_host=https%3A%2F%2Fwww.maxdome.de&Content-Type=|R{SSM}|'
		self.video_url = data['videoUrl']

		return True


class MaxdomeAssets:
	def __init__(self, md_session):		
		self.session = md_session
		self.api_headers = {'accept': 'application/vnd.maxdome.im.v8+json', 'client': 'mxd_package', 'clienttype': 'webportal', 'language': 'de_DE', 'accept-language': 'de_DE', 'platform': 'web', 'Maxdome-Origin': 'maxdome.de'}
		self.page_size = 1000

	def orderAsset(self, assetId, fromStore=False):
		headers = self.api_headers
		headers['content-type'] = 'application/json'
		headers['accept-language'] = 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4'
		headers['Accept-Encoding'] = 'gzip, deflate'
		headers['mxd-session'] = self.session.session.cookies['mxd-bbe-session']
		payload = {'@class':'StartStep','baseData':{'deliveryType':'streaming','licenseType':'rent','quality':'2'}}
		r = self.session.session.post(self.session.api_url + '/interfacemanager-2.1/mxd/mediaauth/' + self.session.customer_id + '/video/' + str(assetId) + '/' + 'sd' + '/start', headers=headers, data=json.dumps(payload))
		if not 'orderId' in r.text:
			return False

		orderId = r.json()['orderId']
		url = self.session.api_url + '/api/mxd/playlist/asset/' + str(assetId) + '?transmissionType[]=mpegDashMultiLang&orderId=' + str(orderId)
		r = self.session.session.get(url, headers=headers)
		data = r.json()
		strmFormat = getStrmFormat(data['playlistItemList'][0]['profileList'][0]['formatList'])
		self.session.license_url = strmFormat['licenseUrl'] + '|User-Agent=Mozilla%2F5.0%20(X11%3B%20Linux%20x86_64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F49.0.2623.87%20Safari%2F537.36&Content-Type=|R{SSM}|'
		self.session.video_url = strmFormat['urlList'][0]['videoUrl']

	def getSeriesCategories(self):
		r = self.session.session.get(self.session.api_url + '/api/navigations/MAIN?client=mxd_package', headers=self.api_headers)
		data = r.json()
		listitems = []		
		for item in data['list'][0]['list'][0]['list'][0]['list']:
			listitems.append({item['title']: item['link']['url']})
		for item in data['list'][0]['list'][0]['list'][1]['list']:
			listitems.append({item['title']: item['link']['url']})
		
		return listitems

	def getMoviesCategories(self):
		r = self.session.session.get(self.session.api_url + '/api/navigations/MAIN?client=mxd_package', headers=self.api_headers)
		data = r.json()
		listitems = []		
		for item in data['list'][0]['list'][1]['list'][0]['list']:
			listitems.append({item['title']: item['link']['url']})
		for item in data['list'][0]['list'][1]['list'][1]['list']:
			listitems.append({item['title']: item['link']['url']})
		
		return listitems

	def getKidsCategories(self):
		r = self.session.session.get(self.session.api_url + '/api/navigations/MAIN?client=mxd_package', headers=self.api_headers)
		data = r.json()
		listitems = []		
		for item in data['list'][0]['list'][2]['list'][0]['list']:
			if item['title'] == 'Kids-Stars':
				continue
			listitems.append({item['title']: item['link']['url']})
		for item in data['list'][0]['list'][2]['list'][1]['list']:
			listitems.append({item['title']: item['link']['url']})
		
		return listitems

	def getKidsStarsCategories(self, path):
		listitems = []
		r = self.session.session.get(self.session.baseurl + path)
		for match in re.findall(r'(?m)<a href="/kids-stars(.*?)"', r.text, re.S):
			listitems.append({'path': match, 'title': ''})
		matches = re.findall(r'(?m)class="trackable" data-tmlc="(.*?)"', r.text, re.S)
		x = len(matches)
		i = 0
		while (i<x): 
			listitems[i]['title'] = unescape(matches[i].replace('online schauen', ''))
			i = i+1

		return listitems

	def getBoughtAssets(self):
		path = '/mein-account/historie?history=2'
		return self.parseHtmlAssets(path=path, use_size=True, opt_pref='r_', select_set=1)

	def getRentAssets(self):
		path = '/mein-account/historie?history=1'
		return self.parseHtmlAssets(path=path, use_size=True, opt_pref='r_', select_set=0)

	def getAssetInformation(self, assetId):
		r = self.session.session.get(self.session.api_url + '/api/assets/' + str(assetId), headers=self.api_headers)
		return r.json()

	def parseAsset(self, assetId):
		data = self.getAssetInformation(assetId)
		listitems = []
		if data['@class'] == 'MultiAssetBundleTvSeries':			
			for season in data['seasons']['assetList']:
				item = {'id': season['id'], 'title': 'Staffel ' + season['number'], 'class': data['@class']} 
				listitems.append(item)
			return listitems
		elif data['@class'] == 'MultiAssetTvSeriesSeason':
			season = '%02d' % int(data['number'])
			assets = self.getEpisodesFromHtml(assetId)
			for episode in assets:
				item = {'id': episode.keys()[0], 'title': episode.values()[0], 'class': data['@class']}
				listitems.append(item)
			return listitems
		elif data['@class'] == 'AssetVideoFilm':
			pass
		elif data['@class'] == 'AssetVideoFilmTvSeries':
			pass

	def parseHtmlAssets(self, path, use_size=True, opt_pref='', select_set=0):
		listitems = []
		opt_char = '?'
		url = self.session.baseurl + path
		if '?' in url:
			opt_char = '&'
		if use_size:
			url = url + opt_char + opt_pref + 'size=' + str(self.page_size)
		print url
		r = self.session.session.get(url)
		page_count = self.getHtmlPageCount(r.text)
		x = 1
		while (x<=page_count):
			data = self.getJsonDataProps(r.text, select_set)
			if not 'assets' in data:
				break
			for item in data['assets']:			
				asset = {'id': item['id'], 'title': unescape(item['title']), 'class': item['@class'], 'poster': item['coverList'][0]['url']}
				listitems.append(asset)
			x = x+1
			if page_count>1:
				url = self.session.baseurl + path + opt_char + opt_pref + 'start=' + str(x)
				if use_size:
					url = url + '&' + opt_pref + 'size=' + str(self.page_size)
				r = self.session.session.get(url)

		return listitems

	def getEpisodesFromHtml(self, assetId):
		items = []
		r = self.session.session.get(self.session.baseurl + '/' + str(assetId))
		page_count = self.getHtmlPageCount(r.text)
		x = 1
		while (x<=page_count):
			count = 0
			soup = BeautifulSoup(r.text)
			matches = soup.findAll('a', {'data-tmlc': 'Asset'})
			while (count<len(matches)):
				episode_title = matches[count].text.strip() + ' ' + matches[count+1].text.strip()
				link = matches[count]['href']
				endpos = link.find('.html')
				startpos = link.rfind('-')+1
				asset_id = link[startpos:endpos]
				items.append({asset_id: episode_title})
				count = count+3
			x = x+1
			if page_count>1:
				r = self.session.session.get(self.session.baseurl + '/' + str(assetId))

		return items

#	def getEpisodesFromHtml(self, assetId):
#		items = []
#		r = self.session.session.get(self.session.baseurl + '/' + str(assetId))
#		page_count = len(re.findall(r'(?m)<a href=\"\?start=(.*?)</a>', r.text, re.S))-1
#		if page_count < 1:
#			page_count = 1
#		x = 1
#		while (x<=page_count):
#			count = 0
#			episodeNames = re.findall(r'(?m)data-tmlc="Asset">(.*?)</a>', r.text, re.S)
#			for match in re.findall(r'(?m)<td class="episode-number">(.*?)</td>', r.text, re.S):
#				name = episodeNames[3*count].strip() + ' ' + episodeNames[(3*count)+1].strip()
#				endpos = match.find('.html')
#				startpos = match.rfind('-', 0, endpos)
#				items.append({match[startpos+1:endpos]: unescape(name)})
#				count = count+1
#			x = x+1
#			if page_count>1:
#				r = self.session.session.get(self.session.baseurl + '/' + str(assetId))
#
#		return items

	def searchAssets(self, term):
		return self.parseHtmlAssets('/suche?search=' + term.replace(' ', '+'), False)

	def getHtmlPageCount(self, html):
		soup = BeautifulSoup(html)
		matches = soup.findAll('a', href=re.compile('\?*start'))
		if len(matches) > 0:
			page_count = matches[len(matches)-2].text
			return int(page_count)

		return 1

	def getJsonDataProps(self, html, idx=0):
		soup = BeautifulSoup(html)
		matches = soup.findAll(attrs={'data-react-props': True})
		if (idx < len(matches)):
			return json.loads(matches[idx]['data-react-props'])

		return None

def unescape(text):
	return HTMLParser.HTMLParser().unescape(text)

def getStrmFormat(formatList):
	useD51 = addon.getSetting('d51')
	d51Available = False
	multiLang = False
	audioType = ''
	resolution = '0'
	resList = {}
	for item in formatList:
		print item['formatType']
		#Audio - order ML|DE|XX
		if item['formatType'].split('|')[1] == 'mu':
			multiLang = True
			audioType = 'mu'
		elif item['formatType'].split('|')[1] == 'de' and not multiLang:
			audioType = 'de'
		elif not multiLang and audioType == '':
			audioType = item['formatType'].split('|')[1]

		#DD5.1 available
		if item['formatType'].split('|')[2][1] == 'd':
			d51Available = True

		#Video - highest resolution
		if int(item['formatType'].split('|')[0]) > int(resolution):
			resolution = item['formatType'].split('|')[0]

		resList[item['formatType']] = item

	audioChannels = '20'	
	if multiLang:
		audioChannels = audioChannels.replace('2', 'x')
	if d51Available and useD51:
		audioChannels = audioChannels.replace('0', 'd')
		if not multiLang:
			audioChannels = audioChannels.replace('2', '5')

	return resList[resolution + '|' + audioType + '|' + audioChannels]
