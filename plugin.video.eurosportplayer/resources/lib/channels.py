# -*- coding: utf-8 -*-

from common import *

class Channels:

    def __init__(self, i):
        self.item = {}
        self.live = 0
        self.label = i['title']
        self.sublabel = i['subtitle']
        self.tvschedules = i['tvschedules']
        self.image = i['logourl']
        self.streams = i['streams'][0]
        self.plot = self.sublabel
        self.date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        self.schedule = self.get_schedule()
        self.update_item()
        
    def get_schedule(self):
        if self.tvschedules:
            return find_current_show(self.tvschedules)
    
    def title(self):
        if not self.sublabel:
            self.live = 1
        if self.live == 1:
            return utfenc(unicode('%s [COLOR red]LIVE[/COLOR] [I]%s[/I]' % (self.label, self.sublabel)))
        else:
            return utfenc(unicode('%s [I]%s[/I]' % (self.label, self.sublabel)))
        
    def schedule_update(self):
        s = self.schedule
        name = s['name']
        if not name:
            name = s['overtitle']
        description = s['description']
        startdate = s['startdate']
        sdate = startdate['technicaldate']
        stime = startdate['time']
        enddate = s['enddate']
        edate = enddate['technicaldate']
        etime = enddate['time']
        audio = self.streams['audio']
        if name and self.tvschedules:
            self.sublabel = name
        self.live = s.get('transmissiontypeid', 0)
        self.plot = utfenc(unicode('%s (%s)\n%s\nStart: %s %s\nEnd: %s %s' % (name,audio,description,sdate,stime,edate,etime)))
        self.item['duration'] = get_duration(s)
        
    def update_item(self):
        if self.schedule:
            self.schedule_update()
        self.item['mode'] = 'play'
        self.item['title'] = clearString(self.title())
        self.item['id'] = self.streams['url']
        self.item['thumb'] = self.image
        self.item['plot'] = clearString(self.plot)
        self.item['date'] = self.date
                            
def find_current_show(schedule):
    now = datetime.datetime.now()
    for s in schedule:
        endtime = convert_date(s['enddate']['datetime'])
        starttime = convert_date(s['startdate']['datetime'])
        if now < endtime and now >= starttime:
            return s

def get_duration(s):
    now = datetime.datetime.now()
    endtime = convert_date(s['enddate']['datetime'])
    return timedelta_total_seconds(endtime-now)
    
def convert_date(dateString):
    date_regex = re.compile('Date\(([0-9]*?)\+([0-9]*?)\)')
    r = date_regex.search(dateString)
    (time, offset) = r.groups()
    time = int(time)
    time = time / 1000
    return datetime.datetime.fromtimestamp(time)