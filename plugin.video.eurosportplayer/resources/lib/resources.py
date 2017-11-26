# -*- coding: utf-8 -*-

from common import *
            
def resources(string):
    if string == 'Today':
        return getString(30221)
    elif string == 'Tomorrow':
        return getString(30222)
    elif string == 'Monday':
        return getString(30223)
    elif string == 'Tuesday':
        return getString(30224)
    elif string == 'Wednesday':
        return getString(30225)
    elif string == 'Thursday':
        return getString(30226)
    elif string == 'Friday':
        return getString(30227)
    elif string == 'Saturday':
        return getString(30228)
    elif string == 'Sunday':
        return getString(30229)
    else:
        return string