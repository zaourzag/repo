# -*- coding: utf-8 -*-

from common import *
            
def resources(str):
    if str == 'Today':
        return getString(30221)
    elif str == 'Tomorrow':
        return getString(30222)
    elif str == 'Monday':
        return getString(30223)
    elif str == 'Tuesday':
        return getString(30224)
    elif str == 'Wednesday':
        return getString(30225)
    elif str == 'Thursday':
        return getString(30226)
    elif str == 'Friday':
        return getString(30227)
    elif str == 'Saturday':
        return getString(30228)
    elif str == 'Sunday':
        return getString(30229)
    else:
        return str