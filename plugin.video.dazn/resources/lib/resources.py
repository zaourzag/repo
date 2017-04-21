# -*- coding: utf-8 -*-

from common import *
            
def resources(str):
    if str == 'CatchUp':
        return getString(30201)
    elif str == 'ComingUp':
        return getString(30202)
    elif str == 'UpComing':
        return getString(30202)
    elif str == 'Editorial':
        return getString(30203)
    elif str == 'Feature':
        return getString(30204)
    elif str == 'Live':
        return getString(30205)
    elif str == 'MostPopular':
        return getString(30206)
    elif str == 'Personal':
        return getString(30207)
    elif str == 'Scheduled':
        return getString(30208)
    elif str == 'Sport':
        return getString(30209)
    elif str == 'Competition':
        return getString(30210)
    elif str == 'Competitor':
        return getString(30211)
    elif str == 'Today':
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