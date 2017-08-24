# -*- coding: utf-8 -*-

import simple_requests as requests
from common import *
from credentials import Credentials

class Client:

    def __init__(self):
        
        self.IDENTITY_URL = global_base + 'v2/user/identity'
        self.USER_URL = global_base + 'v2/user/profile'
        self.TOKEN_URL = global_base + 'token'
        self.GRAPHQL_URL = search_base + 'svc/search/v2/graphql'
        
        self.API_KEY = '2I84ZDjA2raVJ3hyTdADwdwxgDz7r62J8J0W8bE8N8VVILY446gDlrEB33fqLaXD'
        
        self.LANGUAGE = addon.getSetting('language')
        self.COUNTRY = addon.getSetting('country')
        self.ACCESS_TOKEN = addon.getSetting('access_token')
        self.REFRESH_TOKEN = addon.getSetting('refresh_token')
        
        self.HEADERS = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': self.ACCESS_TOKEN
        }
        
        self.DATA = {
            'query': '',
            'operationName': '',
            'variables': {}
        }
        
    def channels(self):
        self.DATA['query'] = '{ onNow: query(index: "eurosport_global_on_now", type: "Airing", page_size: 500) @context(uiLang: "%s") { hits { hit { ... on Airing { type liveBroadcast linear runTime startDate endDate expires genres playbackUrls { href rel templated } channel { callsign } photos { uri width height } mediaConfig { state productType type } titles { language title descriptionLong } } } } } }' % (self.LANGUAGE)
        return requests.post(self.GRAPHQL_URL, headers=self.HEADERS, json=self.DATA).json()
    
    def categories(self):
        self.DATA['query'] = '{ ListByTitle(title: "sports_filter") { list { ... on Category { id: sport sport tags { type displayName } defaultAssetImage { rawImage width height photos { imageLocation width height } } } } } } '
        return requests.post(self.GRAPHQL_URL, headers=self.HEADERS, json=self.DATA).json()
    
    def videos(self, id):
        self.DATA['query'] = '{ sport_%s:query (index: "eurosport_global",sort: new,page: 1,page_size: 100,type: ["Video","Airing"],must: {termsFilters: [{attributeName: "category", values: ["%s"]}]},must_not: {termsFilters: [{attributeName: "mediaConfigState", values: ["OFF"]}]},should: {termsFilters: [{attributeName: "mediaConfigProductType", values: ["VOD"]},{attributeName: "type", values: ["Video"]}]}) @context(uiLang: "%s") { ... on QueryResponse { ...queryResponse }} }fragment queryResponse on QueryResponse {meta { hits }hits {hit { ... on Airing { ... airingData } ... on Video { ... videoData } }}}fragment airingData on Airing {type contentId mediaId liveBroadcast linear partnerProgramId programId runTime startDate endDate expires genres playbackUrls { href rel templated } channel { id parent callsign partnerId } photos { id uri width height } mediaConfig { state productType type } titles { language title descriptionLong descriptionShort episodeName } }fragment videoData on Video {type contentId epgPartnerProgramId programId appears releaseDate expires runTime genres media { playbackUrls { href rel templated } } titles { title titleBrief episodeName summaryLong summaryShort tags { type value displayName } } photos { rawImage width height photos { imageLocation width height } } }' % (id, id, self.LANGUAGE)
        return requests.post(self.GRAPHQL_URL, headers=self.HEADERS, json=self.DATA).json()
    
    def epg(self, prev_date, date):
        self.DATA['query'] = '{ Airings: query(index: "eurosport_global_all", type: "Airing", from: "%sT22:00:00.000Z", to: "%sT21:59:59.999Z", sort: new, page_size: 500) @context(uiLang: "%s") { hits { hit { ... on Airing {type contentId mediaId liveBroadcast linear partnerProgramId programId runTime startDate endDate expires genres playbackUrls { href rel templated } channel { id parent callsign partnerId } photos { id uri width height } mediaConfig { state productType type } titles { language title descriptionLong descriptionShort episodeName } } } } } }' % (prev_date, date, self.LANGUAGE)
        return requests.post(self.GRAPHQL_URL, headers=self.HEADERS, json=self.DATA).json()
    
    def streams(self, url):
        headers = {
            'accept': 'application/vnd.media-service+json; version=1',
            'authorization': self.ACCESS_TOKEN
        }
        json_data = requests.get(url.format(scenario='browser'), headers=headers).json()
        if json_data.get('errors', ''):
            log('[{0}] {1}'.format(addon_id, utfenc(json_data['errors'][0][:100])))
        json_data['token'] = self.ACCESS_TOKEN
        return json_data
    
    def authorization(self, grant_type='refresh_token', token=''):
        if token == '':
            token = addon.getSetting('device_id')
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'authorization': 'Bearer ' + self.API_KEY
        }
        data = {
            'grant_type': grant_type,
            'platform': 'browser',
            'token': token
        }
        return requests.post(self.TOKEN_URL, headers=headers, data=data).json()
        
    def authentication(self, credentials):
        headers = {
            'accept': 'application/vnd.identity-service+json; version=1.0',
            'content-type': 'application/json',
            'authorization': self.authorization(grant_type='client_credentials')['access_token']
        }
        data = {
            "type": "email-password",
            "email": {
                "address": credentials.email
            },
            "password": {
                "value": credentials.password
            }
        }
        return requests.post(self.IDENTITY_URL, headers=headers, json=data).json()
    
    def user(self):
        headers = {
            'accept': 'application/vnd.identity-service+json; version=1.0',
            'content-type': 'application/json',
            'authorization': self.ACCESS_TOKEN
        }
        return requests.get(self.USER_URL, headers=headers).json()
    
    def user_settings(self, data):
        log('[{0}] {1}'.format(addon_id, 'token refreshed'))
        self.ACCESS_TOKEN = data['access_token']
        self.REFRESH_TOKEN = data['refresh_token']
        self.HEADERS['authorization'] = self.ACCESS_TOKEN
        addon.setSetting('access_token', self.ACCESS_TOKEN)
        addon.setSetting('refresh_token', self.REFRESH_TOKEN)
        
    def profile(self):
        json_data = self.user()
        if json_data.get('message', ''):
            log('[{0}] {1}'.format(addon_id, utfenc(json_data['message'][:100])))
            self.user_settings(self.authorization(token=self.REFRESH_TOKEN))
            json_data = self.user()
        properties = json_data['profile']['profileProperty']
        for i in properties:
            name = i['name']
            if name == 'country':
                self.COUNTRY = i['value']
                addon.setSetting('country', self.COUNTRY)
            if name == 'language':
                self.LANGUAGE = i['value']
                addon.setSetting('language', self.LANGUAGE)
        log('[{0}] country: {1} language: {2}'.format(addon_id, self.COUNTRY, self.LANGUAGE))
                
    def login(self):
        code = None
        credentials = Credentials()
        if credentials.email and credentials.password:
            json_data = self.authentication(credentials)
            if json_data.get('message'):
                msg = utfenc(json_data['message'][:100])
            else:
                msg = 'logged in'
                credentials.save()
                code = json_data['code']
            log('[{0}] {1}'.format(addon_id, msg))
        if code:
            self.user_settings(self.authorization(grant_type='urn:mlbam:params:oauth:grant_type:token', token=code))
            self.profile()