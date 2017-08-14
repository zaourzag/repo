# -*- coding: utf-8 -*-

from common import *
from items import Items
from events import Events
from videos import Videos
from playback import Live, Vod

items = Items()

def home_items():
    events = {
        'mode': 'events',
        'title': 'Live',
        'plot': 'Live Matches'
    }
    items.add_item(events)
    features = {
        'mode': 'features',
        'title': 'Features',
        'plot': 'Features Archive'
    }
    items.add_item(features)
    ondemand = {
        'mode': 'ondemand',
        'title': 'On Demand',
        'plot': 'Full Match and Highlights'
    }
    items.add_item(ondemand)
    items.list_items()
    

def event_items(data):
    for i in data:
        items.add_item(Events(i).item)
    items.list_items()
    
def video_items(data):
    length = data['itemsLength']
    total = data['totalVideos']
    _items = data['items']
    for i in _items:
        items.add_item(Videos(i).item)
    items.list_items()
    
def play_live(data):
    items.play_item(Live(data).path)
    
def play_vod(data):
    items.play_item(Vod(data).path)