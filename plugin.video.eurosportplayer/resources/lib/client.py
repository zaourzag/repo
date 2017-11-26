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
        
        self.ACCESS_TOKEN = addon.getSetting('access_token')
        self.REFRESH_TOKEN = addon.getSetting('refresh_token')
        
        self.refresh_token()
        
    def graphql_request(self, url, query='', variables=None):
        if variables is None:
            variables = {}
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': self.ACCESS_TOKEN
        }
        variables.update({
            'language': language,
            'mediaRights': ['GeoMediaRight'],
            'preferredLanguages': [language, 'en']
        })
        post_data = {
            'query': query,
            'operationName': '',
            'variables': variables
        }
        return requests.post(url, headers=headers, json=post_data).json()
        
    def channels(self):
        return self.graphql_request(self.GRAPHQL_URL + '/persisted/query/eurosport/web/Airings/onAir')
    
    def categories(self):
        return self.graphql_request(self.GRAPHQL_URL + '/persisted/query/eurosport/ListByTitle/sports_filter')
    
    def category_all(self):
        return self.graphql_request(self.GRAPHQL_URL + '/persisted/query/eurosport/CategoryAll')
    
    def events(self):
        return self.graphql_request(self.GRAPHQL_URL + '/persisted/query/eurosport/EventPageByLanguage')
    
    def event(self, _id):
        return self.graphql_request(
            url = self.GRAPHQL_URL + '/persisted/query/eurosport/web/EventPageByContentId',
            variables = {
                'contentId': _id,
                'include_media': True,
                'include_images': True
            }
        )

    def videos(self, _id):
        return self.graphql_request(
            url = self.GRAPHQL_URL,
            query = '{ sport_%s:query (index: "eurosport_global",sort: new,page: 1,page_size: 1000,type: ["Video","Airing"],must: {termsFilters: [{attributeName: "category", values: ["%s"]}]},must_not: {termsFilters: [{attributeName: "mediaConfigState", values: ["OFF"]}]},should: {termsFilters: [{attributeName: "mediaConfigProductType", values: ["VOD"]},{attributeName: "type", values: ["Video"]}]}) @context(uiLang: "%s") { ... on QueryResponse { ...queryResponse }} }fragment queryResponse on QueryResponse {meta { hits }hits {hit { ... on Airing { ... airingData } ... on Video { ... videoData } }}}fragment airingData on Airing {type contentId mediaId liveBroadcast linear partnerProgramId programId runTime startDate endDate expires genres playbackUrls { href rel templated } channel { id parent callsign partnerId } photos { id uri width height } mediaConfig { state productType type } titles { language title descriptionLong descriptionShort episodeName } }fragment videoData on Video {type contentId epgPartnerProgramId programId appears releaseDate expires runTime genres media { playbackUrls { href rel templated } } titles { title titleBrief episodeName summaryLong summaryShort tags { type value displayName } } photos { rawImage width height photos { imageLocation width height } } }' % (_id, _id, language)
        )
    
    def epg(self, prev_date, date):
        return self.graphql_request(
            url = self.GRAPHQL_URL + '/persisted/query/eurosport/web/Airings/DateRange',
            variables = {
                'startDate': prev_date+'T22:00:00.000Z',
                'endDate': date+'T21:59:59.999Z'
            }
        )
    
    def license_key(self):
        return '|authorization='+self.ACCESS_TOKEN+'|||plugin://'+addon_id+'/?mode=license_renewal'
    
    def streams(self, url):
        headers = {
            'accept': 'application/vnd.media-service+json; version=1',
            'authorization': self.ACCESS_TOKEN
        }
        data = requests.get(url.format(scenario='browser'), headers=headers).json()
        if data.get('errors', ''):
            log('[{0}] {1}'.format(addon_id, utfenc(data['errors'][0][:100])))
        data['license_key'] = self.license_key()
        return data
    
    def authorization(self, grant_type='refresh_token', token=''):
        if token == '':
            token = addon.getSetting('device_id')
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'authorization': 'Bearer ' + self.API_KEY
        }
        post_data = {
            'grant_type': grant_type,
            'platform': 'browser',
            'token': token
        }
        return requests.post(self.TOKEN_URL, headers=headers, data=post_data).json()
        
    def authentication(self, credentials):
        headers = {
            'accept': 'application/vnd.identity-service+json; version=1.0',
            'content-type': 'application/json',
            'authorization': self.authorization(grant_type='client_credentials')['access_token']
        }
        post_data = {
            "type": "email-password",
            "email": {
                "address": credentials.email
            },
            "password": {
                "value": credentials.password
            }
        }
        return requests.post(self.IDENTITY_URL, headers=headers, json=post_data).json()
    
    def user(self):
        headers = {
            'accept': 'application/vnd.identity-service+json; version=1.0',
            'content-type': 'application/json',
            'authorization': self.ACCESS_TOKEN
        }
        return requests.get(self.USER_URL, headers=headers).json()
    
    def user_settings(self, data):
        self.ACCESS_TOKEN = data.get('access_token', '')
        self.REFRESH_TOKEN = data.get('refresh_token', '')
        addon.setSetting('access_token', self.ACCESS_TOKEN)
        addon.setSetting('refresh_token', self.REFRESH_TOKEN)
    
    def refresh_token(self):
        if self.REFRESH_TOKEN:
            self.user_settings(self.authorization(token=self.REFRESH_TOKEN))
        else:
            self.login()
        
    def profile(self):
        data = self.user()
        properties = data['profile']['profileProperty']
        for i in properties:
            name = i['name']
            if name == 'country':
                addon.setSetting('country', i['value'])
            if name == 'language':
                addon.setSetting('language', i['value'])
                
    def login(self):
        code = None
        credentials = Credentials()
        if credentials.email and credentials.password:
            data = self.authentication(credentials)
            if data.get('message'):
                msg = utfenc(data['message'][:100])
            else:
                msg = 'logged in'
                credentials.save()
                code = data['code']
            log('[{0}] {1}'.format(addon_id, msg))
        if code:
            self.user_settings(self.authorization(grant_type='urn:mlbam:params:oauth:grant_type:token', token=code))
            self.profile()
