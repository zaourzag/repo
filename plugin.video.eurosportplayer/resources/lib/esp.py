# -*- coding: utf-8 -*-

from common import *
from items import Items
        
items = Items()

def channel(data):
    from channels import Channels
    if data.get('PlayerObj', []):
        obj = data['PlayerObj']
        for i in obj:
            if i.get('streams', None):
                items.add(Channels(i).item)
    items.add({'mode':'epg', 'title':getString(30103), 'plot':getString(30103)})
    items.add({'mode':'sports', 'title':getString(30101), 'plot':getString(30102)})
    items.list()

def sport(data):
    from sports import Sports
    if data.get('PlayerObj', []):
        sports = data['PlayerObj']['sports']
        for i in sports:
            items.add(Sports(i).item)
    items.list()
    
def video(data, match):
    from catchups import Catchups
    if data.get('PlayerObj', []):
        catchups = data['PlayerObj']['catchups']
        for i in catchups:
            if str(match) == str(i['sport']['id']):
                items.add(Catchups(i).item)
    items.list()
    
def epg(data):
    from epg import EPG
    if data.get('PlayerObj', []):
        for i in data['PlayerObj']:
            items.add(EPG(i).item)
    items.list()
    
def tvschedule(data, match):
    from tvschedules import TVSchedules
    if data.get('PlayerObj', []):
        for i in data['PlayerObj']:
            if str(match) == str(i['channel']):
                for s in i['tvschedules']:
                    items.add(TVSchedules(s).item)
    items.list()
    
def play(id, data):
    token = ''
    if data.get('PlayerObj', ''):
        token = data['PlayerObj']['token']
    if '?' in id:
        path = '%s&%s' % (id,token)
    else:
        path = '%s?%s' % (id,token)
    items.play(path)