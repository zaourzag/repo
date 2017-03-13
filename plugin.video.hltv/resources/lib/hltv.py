# -*- coding: utf-8 -*-

from common import *
from items import Items

items = Items()
        
def home_items(data):
    from matches import Matches
    home = [
        {
            'mode':'archive',
            'title':'Archive',
            'plot':'CS:GO match archive, complete with all CS:GO pro matches.'
        },
    ]
    for i in home:
        items.add_item(i)
    for each_date in data.split('matchListDateBox'):
        if 'matchListRow' in each_date:
            date = re.search('>(.+?)</div>', each_date).group(1)
            for each_match in re.findall('<div class="matchListRow"(.*?)</a>\s*</div>\s*</div>', each_date, re.DOTALL):
                items.add_item(Matches(each_match, date).item)
    items.list_items()
    
def archive_items(data):
    from archive import Archive
    for each_tr in re.findall('<tr style.+?(title=.*?)</a>\n.+?</td>', data, re.DOTALL):
        items.add_item(Archive(each_tr).item)
    items.list_items()
    
def details_items(data):
    from details import Details
    for each_div in re.findall('(<div class="hotmatchroundbox".*?</div>)', data, re.DOTALL):
        items.add_item(Details(each_div).item)
    items.list_items()    

def play(data):
    from resolver import Resolver
    r = Resolver(data)
    items.play_item(r.resolved_url, r.startpercent)