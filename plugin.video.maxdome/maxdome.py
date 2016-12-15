#!/usr/bin/env python
# coding: utf8

import os
import math
import requests
import json
import pickle
import re
import HTMLParser
from BeautifulSoup import BeautifulSoup
import xbmcaddon, xbmcgui
import library as lib

addon = xbmcaddon.Addon()
mxdlib = lib.Library()

def getAssetClass(asset_class):
    if asset_class.lower() == 'multiassetbundletvseries':
        return 'tvshow'
    elif asset_class.lower() == 'multiassettvseriesseason':
        return 'tvseason'
    elif asset_class.lower() == 'assetvideofilm':
        return 'movie'
    elif asset_class.lower() == 'assetvideofilmtvseries':
        return 'tvepisode'
    elif asset_class.lower() == 'multiassetthemespecial':
        return 'theme'

    return None

class MaxdomeSession:
    def __init__(self, username, password, pathToCookies, region):
        self.session = requests.Session()
        self.cookie_path = pathToCookies
        self.region = region
        self.username = username
        self.password = password
        self.customer_id = ''
        self.payment_type = addon.getSetting('payment').lower()
        self.order_quality = '2'
        self.session.headers.setdefault('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')

        #Maxdome URLs
        self.baseurl = 'https://www.maxdome.' + self.region
        self.api_url = 'https://heimdall.maxdome.de'
        self.login_url = 'https://www.maxdome.' + self.region + '/_ajax/process/login/start/login0'
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
                self.session.cookies['mxd-ua'] = '%7B%22os%22%3A%7B%22name%22%3A%22Linux%22%2C%22version%22%3A%22x86_64%22%7D%2C%22browser%22%3A%7B%22name%22%3A%22Chrome%22%2C%22version%22%3A%2248.0.2564.116%22%2C%22major%22%3A%2248%22%2C%22architecture%22%3A%2232%22%7D%7D'
                with open(self.cookie_path, 'w') as f:
                    pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

        self.Assets = MaxdomeAssets(self)
        #self.getPreferences()

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
        headers = {'accept':'application/vnd.maxdome.im.v8+json', 'Accept-Encoding':'gzip, deflate, sdch', 'Accept-Language':'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4', 'client':'mxd_package', 'clienttype': 'webportal', 'Connection': 'keep-alive', 'content-type':'application/json', 'customerId':self.customer_id, 'language':'de_' + self.region.upper(), 'Maxdome-Origin':'maxdome.' + self.region, 'mxd-session':self.session.cookies['mxd-bbe-session'], 'platform':'web'}
        r = self.session.get(self.api_url + '/interfacemanager-2.1/mxd/customer/' + self.customer_id + '/preference', headers=headers)
        data = r.json()
        print data

    def login(self):
        headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'Accept-Language':'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4', 'connection': 'keep-alive', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://www.maxdome.' + self.region, 'Referer': 'https://www.maxdome.' + self.region}
        payload = {'userId': self.username, 'phrase': self.password, 'autoLogin': 'true'}

        r = self.session.post(self.login_url, headers=headers, data=payload)
        if 'Erfolgreich angemeldet' in r.text:
            return self.isLoggedIn()

        return False

class MaxdomeAssets:
    def __init__(self, md_session):
        self.session = md_session
        self.api_headers = {}
        self.api_headers['accept'] = 'application/vnd.maxdome.im.v8+json'
        self.api_headers['content-type'] = 'application/json'
        self.api_headers['client'] = 'mxd_store'
        self.api_headers['clienttype'] = 'webportal'
        self.api_headers['language'] = 'de_' + self.session.region.upper()
        self.api_headers['accept-language'] = 'de_DE'
        self.api_headers['accept-encoding'] = 'gzip, detach'
        self.api_headers['platform'] = 'web'
        self.api_headers['Maxdome-Origin'] = 'maxdome.' + self.session.region
        self.api_headers['customerId'] = self.session.customer_id
        self.api_headers['mxd-session'] = self.session.session.cookies.get('mxd-bbe-session', domain='.maxdome.' + self.session.region)
        self.page_size = 1000

    def isPackageContent(self, asset_info):
        if 'packageList' in asset_info:
            for item in asset_info['packageList']:
                if 'premium_basic' in item:
                    return True

        return False

    def getSalesLabel(self, text):
        if not '<strike>' in text or not '</strike>' in text:
            return text
        rm_start = text.index('<strike>')
        rm_end = text.index('</strike>')+len('</strike>')

        return text.replace(text[rm_start:rm_end], '')

    def getSalesOptions(self, asset_info):
        listitems = []
        sale_props = asset_info['salesPropertiesContainer']['salesPropertiesRentSD']
        sale_label = self.getSalesLabel(sale_props['buttonText'])
        if sale_props['availableStatus'] == 'available':
            listitems.append({'orderType':'rent', 'orderQuality': 'sd', 'label': 'SD Leihen fuer ' + sale_label})
        sale_props = asset_info['salesPropertiesContainer']['salesPropertiesRentHD']
        sale_label = self.getSalesLabel(sale_props['buttonText'])
        if sale_props['availableStatus'] == 'available':
            listitems.append({'orderType':'rent', 'orderQuality': 'hd', 'label': 'HD Leihen fuer ' + sale_label})
        sale_props = asset_info['salesPropertiesContainer']['salesPropertiesBuySD']
        sale_label = self.getSalesLabel(sale_props['buttonText'])
        if sale_props['availableStatus'] == 'available':
            listitems.append({'orderType':'buy', 'orderQuality': 'sd', 'label': 'SD Kaufen fuer ' + sale_label})
        sale_props = asset_info['salesPropertiesContainer']['salesPropertiesBuyHD']
        sale_label = self.getSalesLabel(sale_props['buttonText'])
        if sale_props['availableStatus'] == 'available':
            listitems.append({'orderType':'buy', 'orderQuality': 'hd', 'label': 'HD Kaufen fuer ' + sale_label})

        return listitems

    def addToNotepad(self, assetid):
        r = self.session.session.post(self.session.baseurl + '/_ajax/notepad/' + str(assetid))

    def deleteFromNotepad(self, assetid):
        r = self.session.session.delete(self.session.baseurl + '/_ajax/notepad/' + str(assetid))

    def checkAvsPin(self, base_data):
        dlg = xbmcgui.Dialog()
        pin = dlg.input('Altersfreigabe PIN', type=xbmcgui.INPUT_NUMERIC)        
        headers = self.api_headers
        headers['accept-language'] = 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4'
        url = '%s/interfacemanager-2.1/mxd/mediaauth/%s/video/%s/%s/checkAvsPin' % (self.session.api_url, self.session.customer_id, str(base_data['assetId']), base_data['orderedQuality'])
        payload = {'@class':'CheckAvsPinAnswerStep','baseData': base_data, 'pin': pin}
        r = self.session.session.post(url, headers=headers, data=json.dumps(payload))
        data = r.json()
        if '@class' in data:
            if data['@class'] == 'AvsInvalidPinStep':
                xbmcgui.Dialog().notification('Maxdome', 'Eingegebene PIN ist ungültig', xbmcgui.NOTIFICATION_ERROR, 2000, True)
                return False

        return data

    def showPaymentOptions(self, data):
        items = []
        for opt in data['paymentMethodList']:
            items.append(opt['title'])
        dlg = xbmcgui.Dialog()
        dlg.select('Zahlungsart', items)
        

    def orderAsset(self, assetId, buyAsset=False, isHd=False, order_option='', orderType='rent', orderQuality='sd'):
        headers = self.api_headers
        headers['accept-language'] = 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4'
        url = '%s/interfacemanager-2.1/mxd/mediaauth/%s/video/%s/%s/start' % (self.session.api_url, self.session.customer_id, str(assetId), orderQuality)
        payload = {'@class':'StartStep','baseData':{'deliveryType':'streaming','licenseType':orderType,'quality':self.session.order_quality}}
        r = self.session.session.post(url, headers=headers, data=json.dumps(payload))
        data = r.json()
        if '@class' in data:
            if data['@class'] == 'SelectPaymentQuestionStep':
                #TODO Verschiedene Zahlungsmethoden anbieten
                return data
            elif data['@class'] == 'CheckAvsPinQuestionStep':
                data = self.checkAvsPin(data['baseData'])
                if not data:
                    return False

        elif 'errorCode' in data:
            if 'MediaAuthNoLicenseAvailable' in data['message']:
                pass

        if not 'orderId' in data:
            return False

        orderId = data['orderId']
        url = self.session.api_url + '/api/mxd/playlist/asset/' + str(assetId) + '?transmissionType[]=mpegDashMultiLang&orderId=' + str(orderId)
        r = self.session.session.get(url, headers=headers)
        data = r.json()
        strmFormat = getStrmFormat(data['playlistItemList'][0]['profileList'][0]['formatList'])
        self.session.license_url = strmFormat['licenseUrl'] + '|User-Agent=Mozilla%2F5.0%20(X11%3B%20Linux%20x86_64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F49.0.2623.87%20Safari%2F537.36|R{SSM}|'
        self.session.video_url = strmFormat['urlList'][0]['videoUrl']

        return True

    def processPayment(self, assetid, orderType, orderQuality):
        headers = self.api_headers
        headers['accept-language'] = 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4'
        url = '%s/interfacemanager-2.1/mxd/mediaauth/%s/video/%s/%s/selectPayment' % (self.session.api_url, self.session.customer_id, str(assetid), orderQuality)
        payload = {'@class':'SelectPaymentAnswerStep','baseData':{'deliveryType':'streaming','licenseType':orderType,'quality':self.session.order_quality},'selectedPaymentType':self.session.payment_type}
        r = self.session.session.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code != 200:
            return False

        return True

    def confirmPayment(self, assetid, orderType, orderQuality):
        headers = self.api_headers
        headers['accept-language'] = 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4'
        url = '%s/interfacemanager-2.1/mxd/mediaauth/%s/video/%s/%s/confirm%s' % (self.session.api_url, self.session.customer_id, str(assetid), orderQuality, self.session.payment_type.title())
        payload = {'@class':'Confirm' + self.session.payment_type.title() + 'AnswerStep','baseData':{'deliveryType':'streaming','licenseType':orderType,'quality':self.session.order_quality},'selectedPaymentType':self.session.payment_type}
        r = self.session.session.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code != 200:
            return False

        return True

    def getAssetInformation(self, assetId):
        r = self.session.session.get(self.session.api_url + '/api/assets/' + str(assetId), headers=self.api_headers)
        return r.json()

    def parseHtmlAssets(self, path, use_size=True, opt_pref='', select_set=0):
        listitems = []
        opt_char = '?'
#        url = self.session.baseurl + path
        url = path
        if '?' in url:
            opt_char = '&'
        if use_size and ('size=' not in path):
            url = url + opt_char + opt_pref + 'size=' + str(self.page_size)
        r = self.session.session.get(url)
        page_count = self.getHtmlPageCount(r.text)
        data = self.getJsonDataProps(r.text, select_set)
        if not data:
            return listitems
        for item in data['assets']:
            asset = {'id': item['id'], 'title': unescape(item['title']), 'class': item['@class'], 'poster': item['coverList'][0]['url'], 'green': item['green']}
            print asset
            listitems.append(asset)

        nextPagePath = self.getHtmlNextPage(r.text)
        if nextPagePath:
            url = url[0:url.rfind('?')] + nextPagePath
            li = {'class': 'list', 'title': 'Mehr...', 'url': url}
            listitems.append(li)

        return listitems


    def parseHtmlAssetsBak(self, path, use_size=True, opt_pref='', select_set=0):
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
            for item in data['assets']:
                listitems.append(item['id'])
            x = x+1
            if page_count>1:
                url = self.session.baseurl + path + opt_char + opt_pref + 'start=' + str(x)
                if use_size:
                    url = url + '&' + opt_pref + 'size=' + str(self.page_size)
                r = self.session.session.get(url)

        return listitems

    def isPlayableAsset(self, assetId):
        r = self.session.session.get(self.session.baseurl + '/' + str(assetId))
        soup = BeautifulSoup(r.text)
        data = self.getJsonDataProps(r.text, idx=0, field='green')
        return data['asset']['green']

    def getHtmlPageCount(self, html):
        soup = BeautifulSoup(html)
        matches = soup.findAll('a', href=re.compile('\?*start'))
        if len(matches) > 0:
            page_count = matches[len(matches)-2].text
            return int(page_count)

        return 1

    def getHtmlNextPage(self, html):
        soup = BeautifulSoup(html)
        matches = soup.findAll('li', {'class': 'component--pagination-last-child '})
        if len(matches) > 0:
            return matches[0].find('a')['href']

        return None

    def getJsonDataProps(self, html, idx=0, field=''):
        soup = BeautifulSoup(html)
        matches = soup.findAll(attrs={'data-react-props': True})
        while (idx < len(matches)):
            if field == '':
                return json.loads(matches[idx]['data-react-props'])
            else:
                data = json.loads(matches[idx]['data-react-props'])
                if 'asset' in data:
                    if field in data['asset']:
                        return data
                idx = idx+1

        return None

    def exportAsset(self, assetId):
        asset_info = self.getAssetInformation(assetId)
        asset_class = getAssetClass(asset_info['@class'])
        if asset_class == 'tvshow':
            #parse seasons
            for season in asset_info['seasons']['assetList']:
                self.exportAsset(season['id'])
        elif asset_class == 'tvseason':
            episodes = self.getEpisodesFromHtml(asset_info['id'])
            for ep in episodes:
                self.exportAsset(ep.keys()[0])
        elif asset_class == 'tvepisode':
            mxdlib.addEpisode(asset_info)
        elif asset_class == 'movie':
            mxdlib.addMovie(asset_info)

    def getAssets2(self, query, start=0):
        res_list = []
        pageStart = 1
        if start>0:
            pageStart = start
        url = self.session.api_url + '/api/mxd/assets?filter[]=' + query + '&pageSize=' + str(self.page_size) + '&pageStart=' + str(pageStart)
        r = self.session.session.get(url, headers=self.api_headers)
        data = r.json()
        page_idx = data['pageInfo']['start']
        page_size = data['pageInfo']['size']
        if page_size < 1:
            return res_list
        page_count = math.ceil(float(data['pageInfo']['total'])/float(page_size))
        
        res_list = data['assetList']
        while (start<1 and page_idx<page_count):
            for item in self.getAssets(query, start=page_idx+1):
                res_list.append(item)
            page_idx = page_idx+1
            
        return res_list

    def getAssets(self, query, page_start=1):
        url = self.session.api_url + '/api/mxd/assets?filter[]=' + query + '&pageSize=' + str(self.page_size) + '&pageStart=' + str(page_start)
        r = self.session.session.get(url, headers=self.api_headers)
        data = r.json()
        return data

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
