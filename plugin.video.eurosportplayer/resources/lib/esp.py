# -*- coding: utf-8 -*-

from common import *
from items import Items
from context import Context

items = Items()

def channel(data):
    from hits import Hits
    hits = data['data']['Airings']
    for i in hits:
        item = Hits(i).item
        if item.get('id'):
            items.add(item)
    date = epg_date()
    prev_date = get_prev_day(date)
    items.add({'mode':'epg', 'title':getString(30103), 'plot':getString(30103), 'id':date.strftime(date_format), 'params':prev_date.strftime(date_format)})
    items.add({'mode':'sports', 'title':getString(30101), 'plot':getString(30102)})
    items.add({'mode':'events', 'title':getString(30104), 'plot':getString(30104)})
    items.list(sort=True)

def sport(data):
    from sports import Sports
    items.add({'mode':'all_sports', 'title':getString(30105).upper(), 'plot':getString(30105)})
    hits = data['data']['sports_filter']['list']
    for i in hits:
        items.add(Sports(i).item)
    items.list(sort=True)

def all_sports(data):
    from sports import Sports
    hits = data['data']['CategoryAll']
    for i in hits:
        item = Sports(i).item
        if item.get('thumb') and item.get('id'):
            items.add(item)
    items.list(sort=True)

def events(data):
    from events import Events
    hits = data['data']['EventPageByLanguage']
    for i in hits:
        items.add(Events(i).item)
    items.list()

def event(data):
    from hits import Hits
    media = data['data']['EventPageByContentId']['media']
    for m in media:
        hits = m['videos']
        for i in hits:
            items.add(Hits(i, event=True).item)
    items.list()

def video(data, id):
    from hits import Hits
    sport_id = 'sport_{0}'.format(id)
    hits = data['data'][sport_id]['hits']
    for i in hits:
        hit = i['hit']
        item = Hits(hit).item
        if item.get('id'):
            items.add(item)
    items.list()

def epg(data, prev_date, date):
    from resources import resources
    from hits import Hits

    def date_item(params, id):
        return {
            'mode': 'epg',
            'title': '{0} {1}'.format(resources(id.strftime('%A')), id.strftime(date_format)),
            'plot': '{0} {1}'.format(resources(epg_date(date).strftime('%A')), epg_date(date).strftime(date_format)),
            'id': id.strftime(date_format),
            'params': params.strftime(date_format),
            'cm': cm
        }

    update = False if date == epg_date().strftime(date_format) else True
    cm = Context().epg_date()
    
    items.add(date_item(get_prev_day(epg_date(prev_date)), epg_date(prev_date)))
    hits = data['data']['Airings']
    hits = sorted(hits, key=lambda k: k.get('startDate'))
    for i in hits:
        items.add(Hits(i, epg=True).item)
    items.add(date_item(epg_date(date), get_next_day(epg_date(date))))
    items.list(upd=update)
    
def play(data):
    if data.get('stream'):
        for i in data['stream']:
            path = data['stream'][i].replace('desktop','wired50')
            break
        key = data['license_key']
        items.play(path, key)
    
def license_renewal(license_key):
    items.add_token(license_key)