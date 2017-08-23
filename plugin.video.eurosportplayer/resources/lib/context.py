# -*- coding: utf-8 -*-

from common import *
from resources import resources

class Context:

    def __init__(self):
        self.cm = []
        
    def epg_date(self):
        d = {
            'mode': 'epg',
            'id': 'date'
        }
        self.cm.append( (utfenc(getString(30230)), 'ActivateWindow(Videos, %s)' % build_url(d)) )
        return self.cm