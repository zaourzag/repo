# -*- coding: utf-8 -*-

from common import *
from items import Items

items = Items()

def rails_items(data, id):
    from rails import Rails
    for i in data.get('Rails', []):
        items.add_item(Rails(i).item)
    items.list_items()
    
def rail_items(data):
    from tiles import Tiles
    focus = data.get('StartPosition', False)
    for i in data.get('Tiles', []):
        item = Tiles(i).item
        cm = []
        if item.get('cm', None):
            cm_items = context_items(item['cm'])
            for i in cm_items:
                d = {
                    'mode': 'play_context',
                    'title': i['title'],
                    'id': i.get('id', ''),
                    'params': i.get('params','')
                }
                cm.append( (i['type'], 'XBMC.RunPlugin(%s)' % build_url(d)) )
                if len(cm) == 3:
                    break
            item['cm'] = cm
        items.add_item(item)
    items.list_items(focus)
    
def context_items(data):
    cm_items = []
    from tiles import Tiles
    for i in data:
        if i.get('Videos', []):
            cm_items.append(Tiles(i).item)
    return cm_items
    
def playback(data, name=False, context=False):
    from playback import Playback
    items.play_item(Playback(data), name, context)