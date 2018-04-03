# coding=utf-8
#
#
# 	 ZapiSession
# 	(c) 2014 Pascal Nançoz
# 	modified by Daniel Griner
#

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, re, base64,sys
import urllib, urllib2
import json

__addon__ = xbmcaddon.Addon()
__addonId__=__addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
DEBUG = __addon__.getSetting('debug')

def debug(s):
	if DEBUG: xbmc.log(str(s), xbmc.LOGDEBUG)

if sys.version_info > (2, 7, 9):
	import ssl
	ssl._create_default_https_context = ssl._create_unverified_context
	
class ZapiSession:
	
	ZAPIUrl = None
	DATA_FOLDER = None
	COOKIE_FILE = None
	SESSION_FILE = None
	ACCOUNT_FILE = None
	ACCOUNT_JSON = None
	HttpHandler = None
	Username = None
	Password = None
	SessionData = None
	AccountData = None
	
	def __init__(self, dataFolder):
		self.DATA_FOLDER = dataFolder
		self.COOKIE_FILE = os.path.join(dataFolder, 'cookie.cache')
		self.SESSION_FILE = os.path.join(dataFolder, 'session.cache')
		self.ACCOUNT_FILE = os.path.join(dataFolder, 'account.cache')
		self.ACCOUNT_JSON = os.path.join(dataFolder, 'account.json' )
		self.APICALL_FILE = os.path.join(dataFolder, 'apicall.cache')
		self.HttpHandler = urllib2.build_opener()
		self.HttpHandler.addheaders = [('Content-type', 'application/x-www-form-urlencoded'), ('Accept', 'application/json')]

	def init_session(self, username, password, api_url="https://zattoo.com"):
		self.Username = username
		self.Password = password
		self.ZAPIUrl = api_url
		return self.restore_session() or self.renew_session()

	def restore_session(self):
		if os.path.isfile(self.COOKIE_FILE) and os.path.isfile(self.ACCOUNT_FILE) and os.path.isfile(self.SESSION_FILE):
			with open(self.ACCOUNT_FILE, 'r') as f:
				accountData = json.loads(base64.b64decode(f.readline()))
			if accountData['success'] == True:
				self.AccountData = accountData
				with open(self.COOKIE_FILE, 'r') as f:
					self.set_cookie(base64.b64decode(f.readline()))
				with open(self.SESSION_FILE, 'r') as f:
					self.SessionData = json.loads(base64.b64decode(f.readline()))
				return True
		return False

	def extract_sessionId(self, cookieContent):
		if cookieContent is not None:
			return re.search("beaker\.session\.id\s*=\s*([^\s;]*)", cookieContent).group(1)
		return None

	def get_accountData(self):
		accountData={}
		if os.path.isfile(self.ACCOUNT_FILE):
			with open(self.ACCOUNT_FILE, 'r') as f:
				accountData = json.loads(base64.b64decode(f.readline()))
		return accountData

	def persist_accountData(self, accountData):
		with open(self.ACCOUNT_FILE, 'w') as f:
			f.write(base64.b64encode(json.dumps(accountData)))
		#with open(self.ACCOUNT_JSON, 'w') as f:
			#f.write(json.dumps(accountData))

	def persist_sessionId(self, sessionId):
		with open(self.COOKIE_FILE, 'w') as f:
			f.write(base64.b64encode(sessionId))
			
	def persist_sessionData(self, sessionData):
		with open(self.SESSION_FILE, 'w') as f:
			f.write(base64.b64encode(json.dumps(sessionData)))



	def set_cookie(self, sessionId):
		self.HttpHandler.addheaders.append(('Cookie', 'beaker.session.id=' + sessionId))

	def request_url(self, url, params):
		try:
			response = self.HttpHandler.open(url, urllib.urlencode(params) if params is not None else None)
			if response is not None:
				sessionId = self.extract_sessionId(response.info().getheader('Set-Cookie'))
				if sessionId is not None:
					self.set_cookie(sessionId)
					self.persist_sessionId(sessionId)
				return response.read()
		except Exception:
			pass
		return None

	# zapiCall with params=None creates GET request otherwise POST

	def exec_zapiCall(self, api, params, context='default'):
		#url = self.ZAPIAuthUrl + api if context == 'session' else self.ZAPIUrl + api
		url = self.ZAPIUrl + api
		#debug( "ZapiCall  " + str(url))
		content = self.request_url(url, params)
		if content is None and context != 'session' and self.renew_session():
			content = self.request_url(url, params)
		if content is None:
			return None
		try:
			resultData = json.loads(content)
			return resultData

        
		except Exception:
			pass
		return None

	def fetch_appToken(self):
		debug("ZapiUrL= "+str(self.ZAPIUrl))
		try:
			handle = urllib2.urlopen(self.ZAPIUrl + '/')
		except:
			handle = urllib.urlopen(self.ZAPIUrl + '/')
		html = handle.read()
		return re.search("window\.appToken\s*=\s*'(.*)'", html).group(1)
		

	def session(self):
		api = '/zapi/session/hello'
		params = {"client_app_token" : self.fetch_appToken(),
				  "uuid"	: "d7512e98-38a0-4f01-b820-5a5cf98141fe",
				  "lang"	: "en",
				  "format"	: "json"}
		sessionData = self.exec_zapiCall(api, params, 'session')
		if sessionData is not None:
			self.SessionData = sessionData
			self.persist_sessionData(sessionData)
			return True
		return False

	def login(self):
		api = '/zapi/account/login'
		params = {"login": self.Username, "password" : self.Password}
		accountData = self.exec_zapiCall(api, params, 'session')
		if accountData is not None:
			self.AccountData = accountData
			self.persist_accountData(accountData)
			return True
		return False

	def renew_session(self):
		return self.session() and self.login()

