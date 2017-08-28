#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Tristan Fischer (sphere@dersphere.de)
#     Copyright (C) 2017 mdmdmdmdmd
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys
from urllib import urlencode
from urllib2 import urlopen, Request, HTTPError, URLError
from urlparse import urlsplit, parse_qsl
from bs4 import BeautifulSoup

if sys.version_info >= (2, 7):
    import json
else:
    import simplejson as json


API_URL = 'http://dokumonster.de/wp-json/wp/v2/'


class NetworkError(Exception):
    pass


class ApiError(Exception):
    pass


class DokuMonsterApi():

    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'

    def __init__(self, default_count=None):
        self.default_count = default_count or 50

    def get_tags(self, page='1'):
        json_data, total_count = self._get_items('tags', page=page)
        items = [{
            'id': tag.get('id'),
            'name': tag.get('name'),
            'count': tag.get('count')
        } for tag in json_data]
        return items, total_count

    def get_topics(self, page='1'):
        topics = ['82', '267', '2391', '17', '24', '117', '79', '122', '28', '408', '1832', '58', '21', '216', '33',
                  '377', '1685', '107', '102', '48', '287', '202', '38', '39', '42', '325', '47', '110', '111', '103',
                  '85', '7', '337', '123', '105', '66', '163', '53', '358', '180', '2652', '126', '178', '182', '114',
                  '26', '476', '13', '233', '22']
        items = []
        for topic in topics:
            tag, _ = self._get_items('tags/%s' % topic)
            item = {
                'id': tag.get('id'),
                'name': tag.get('name'),
                'count': tag.get('count')
            }
            items.append(item)
        return items, str(len(topics))

    def get_top_docus(self, page='1', **kwargs):
        # json_data, total_count = self._get_items('posts', path=kwargs['path'], page=page)
        # items = [{
        #     'online': docu['date'],
        #     'title': docu['title']['rendered'],
        #     'description': docu['content']['rendered'],
        #     'id': docu['id'],
        #     'link': docu['link'].replace('\\', '')
        # } for docu in json_data]
        # return items, total_count
        # FIXME: might have to parse html of 'top-dokus' page :(
        pass

    def get_newest_docus(self, page='1'):
        json_data, total_count = self._get_items('posts', order='desc', page=page)
        items = [{
            'online': docu['date'],
            'title': BeautifulSoup(docu['title']['rendered'], 'html.parser'),
            'description': docu['content']['rendered'],
            'id': docu['id'],
            'link': docu['link'].replace('\\', '')
        } for docu in json_data]
        return items, total_count

    def get_docus_by_initial(self, initial, page='1'):
        # TODO
        pass

    def get_docus_by_tag(self, page='1', **kwargs):
        json_data, total_count = self._get_items('posts', tags=kwargs['tag'], page=page, order='desc')
        items = [{
            'online': docu['date'],
            'title': BeautifulSoup(docu['title']['rendered'], 'html.parser'),
            'description': docu['content']['rendered'],
            'id': docu['id'],
            'link': docu['link'].replace('\\', '')
        } for docu in json_data]
        return items, total_count

    def get_docus_by_query(self, query, page='1'):
        # TODO
        pass

    def get_docu(self, docu_link):
        html = self._geturl(docu_link).read()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.head.title.string.split(' | ')[0]
        match = soup.find(id='stage-player')
        if match is not None:
            url = match.get('src')
            id = urlsplit(url).path[7:]
        else:
            url = soup.find(id='stage').a.get('href')
            id = parse_qsl(urlsplit(url).query)[0][1]
        item = {
            'source': 'youtube.com',
            'type': 'video',
            'id': id,
            'title': title
        }
        return item

    def _get_items(self, path, **kwargs):
        params = {}
        valid_kwargs = (
            'sort', 'tags', 'query', 'initial',
            'order', 'per_page', 'offset', 'page'
        )
        for key, val in kwargs.items():
            if key in valid_kwargs:
                params[key] = val
        if not 'per_page' in params:
            params['per_page'] = self.default_count
        page = params.pop('page', False)
        if page:
            params['offset'] = (int(page) - 1) * params['per_page']
        json_data, total_count = self.__api_call(path=path, params=params)
        return json_data, total_count

    def _geturl(self, url):
        hdr = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        req = Request(url, headers=hdr)
        log('Opening URL: %s' % url)
        try:
            response = urlopen(req)
        except HTTPError, error:
            raise NetworkError('HTTPError: %s' % error)
        except URLError, error:
            raise NetworkError('URLError: %s' % error)
        return response

    def __api_call(self, path, params=None):
        url = API_URL + path
        if params:
            url += '?%s' % urlencode(params)
        response = self._geturl(url)
        data = response.read()
        log('got %d bytes' % len(data))
        json_data = json.loads(data)
        total_count = response.info().get('X-WP-Total')
        return json_data, total_count


def log(msg):
    print('[DokuMonsterApi]: %s' % msg)


if __name__ == '__main__':
    # API testing
    api = DokuMonsterApi()

    # print 'Testing get_tags'
    # tags, count = api.get_tags()
    # remaining = int(count)
    # page = 1
    # list = []
    # while remaining > 0:
    #     tags, count = api.get_tags(page=str(page))
    #     for tag in tags:
    #         list.append({'id': tag['id'], 'name': tag['name'], 'count': tag['count']})
    #     remaining -= 50
    #     page += 1
    # for item in list:
    #     print 'id: %s name: %s' % (item['id'], item['name'])
    # assert tags
    # print count
    # for tag in tags:
    #     print '<Tag:%s>' % repr(tag)
    # items, _ = api.get_docus_by_tag(tag='1787')
    link = 'http://dokumonster.de/sehen/skandinavien-von-oben-norwegen-ardndr-doku/'
    print link
    media = api.get_docu(link)
    url = media.get('title')
    print url
    items, _ = api.get_docus_by_tag(tag='476')
    for item in items:
        print item['online']
    # print 'Testing get_newest_docus'
    # docus = api.get_newest_docus()
    # assert docus
    # for docu in docus[0:2]:
    #     print '<Docu:%s>' % repr(docu)
    #
    # print 'Testing get_popular_docus'
    # docus = api.get_popular_docus()
    # assert docus
    # for docu in docus[0:2]:
    #     print '<Docu:%s>' % repr(docu)
    #
    # print 'Testing get_top_docus'
    # docus = api.get_top_docus()
    # assert docus
    # for docu in docus[0:2]:
    #     print '<Docu:%s>' % repr(docu)
