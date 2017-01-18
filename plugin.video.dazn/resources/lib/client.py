# -*- coding: utf-8 -*-

import simple_requests as requests
from .common import *

import xbmc
   
def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
    
class Client:

    def __init__(self):
        self.TOKEN      = token
        self.POST_DATA  = {}
    
        self.HEADERS    = {
                            "Content-Type" : "application/json",
                            "Referer"      :  base_url,
                            }
                            
        self.PARAMS     = {
                            "$format"      : "json",
                            "LanguageCode" : "'%s'" % language,
                            "Country"      : "'%s'" % country,
                            }
                            
        self.STARTUP    = api_base + "/Startup"
        self.RAIL       = api_base + "/Rail"
        self.RAILS      = api_base + "/Rails"
        self.PLAYBACK   = api_base + "/Playback"
        self.SIGNIN     = api_base + "/SignIn"
        self.SIGNOUT    = api_base + "/SignOut"
        self.REFRESH    = api_base + "/RefreshAccessToken"
        
    def rails(self, id, params=""):
        self.PARAMS["groupId"] = "'%s'" % id
        self.PARAMS["params"]  = "'%s'" % params
        return self.request(self.RAILS)
        
    def rail(self, id, params=""):
        self.PARAMS["id"]      = "'%s'" % id
        self.PARAMS["params"]  = "'%s'" % params
        return self.request(self.RAIL)
        
    def playback_data(self, id):
        self.POST_DATA = {
                            "AssetId"            : id,
                            "Format"             : "MPEG-DASH",
                            "PlayerId"           : uniq_id(device_id),
                            "Secure"             : "true",
                            "PlayReadyInitiator" : "false",
                            "BadManifests"       : [],
                            "LanguageCode"       : "%s" % language,
                            }
        return self.request(self.PLAYBACK)
        
    def playback(self, id):
        self.HEADERS["Authorization"] = "Bearer " + self.TOKEN
        data = self.playback_data(id)
        if data.get("odata.error", None):
            self.errorHandler(data)
            if self.TOKEN:
                data = self.playback_data(id)
        return data
        
    def setToken(self, auth, result):
        log("[%s] signin: %s" % (addon_id, result))
        if auth:
            self.TOKEN = auth["Token"]
            self.HEADERS["Authorization"] = "Bearer " + self.TOKEN
        else:
            self.TOKEN = ""
            dialog.ok("DAZN", result)
        if result == "HardOffer":
            dialog.ok("DAZN", getString(30161))
        addon.setSetting("token", self.TOKEN)
        
    def signIn(self):
        if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) and len(password) > 4:
            self.POST_DATA = {
                                "Email"    : utfenc(email),
                                "Password" : utfenc(password),
                                "DeviceId" : uniq_id(device_id),
                                "Platform" : "web",
                                }
            data = self.request(self.SIGNIN)
            if data.get("odata.error", None):
                self.errorHandler(data)
            else:
                if data["AuthTokens"]:
                    auth = data["AuthTokens"][0]
                else:
                    auth = ""
                self.setToken(auth, data.get("Result", "SignInError"))
        else:
            addon.openSettings()
            
    def signOut(self):
        self.HEADERS["Authorization"] = "Bearer " + self.TOKEN
        self.POST_DATA = {
                            "DeviceId" : uniq_id(device_id)
                            }
        r = self.request(self.SIGNOUT)
        
    def refreshToken(self):
        self.POST_DATA = {
                            "OriginalToken" : self.TOKEN
                            }
        data = self.request(self.REFRESH)
        debug("refreshToken DATA :" )
        debug(data)
        if data.get("odata.error", None):
            self.errorHandler(data)
        else:
            self.setToken(data["AuthToken"], data.get("Result", "RefreshAccessTokenError"))
            
    def startUp(self):
        self.POST_DATA = {
                            "LandingPageKey":"generic",
                            "Languages"     :"",
                            "Platform"      :"web",
                            "Manufacturer"  :"",
                            "PromoCode"     :"",
                            }
        data = self.request(self.STARTUP)
        if data:
            allowed = data["Region"]["isAllowed"]
            if allowed == True:
                addon.setSetting("language", data["Region"]["Language"])
                addon.setSetting("country", data["Region"]["Country"])
                if not self.TOKEN:
                    self.signIn()
            else:
                dialog.ok("DAZN", getString(30101))
            self.POST_DATA  = {}
        else:
            self.TOKEN = ""
        
    def request(self, url):
        debug("Start request")
        debug("URL :"+url)
        debug("Data :")
        debug(self.POST_DATA)
        debug("HEADER :")
        debug(self.HEADERS)
        debug("Params :")
        debug (self.PARAMS)        
        if self.POST_DATA:
            r = requests.post(url, headers=self.HEADERS, data=self.POST_DATA, params=self.PARAMS)
        else:
            r = requests.get(url, headers=self.HEADERS, params=self.PARAMS)
        debug("Return")
        debug("Code :"+str(r.status_code))
        debug("JSON :")
        debug(r.json())
        if r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        else:
            if not r.status_code == 204:
                log("[%s] error: json request (%s, %s)" % (addon_id, str(r.status_code), r.headers.get("content-type", "")))
            return {}
            
    def errorHandler(self, data):
        msg  = data["odata.error"]["message"]["value"]
        code = data["odata.error"]["code"]
        log("[%s] error: %s (%s)" % (addon_id, msg, code))
        if code == "1":
            self.refreshToken()
        elif code == "2" or code.lower() == "signin":
            self.signIn()
        elif code == "7":
            dialog.ok("DAZN", getString(30107))
        elif code == "10008":
            dialog.ok("DAZN", getString(30108))
        elif code == "InvalidAccount" or code == "invalidPassword":
            dialog.ok("DAZN", getString(30151))
        elif code == "unableFindEmail":
            dialog.ok("DAZN", getString(30152))
        elif code == "passwords_doesnt_match":
            dialog.ok("DAZN", getString(30153))
        else:
            dialog.ok("DAZN", msg)