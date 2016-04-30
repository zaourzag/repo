# -*- coding: utf-8 -*-
import urllib2
from re import findall

"""
WIP
"""

def get_country_code(language = 'de'):
    api_url = 'http://www.arte.tv/artews/services/geolocation'
    try:
        xml_data = urllib2.urlopen(api_url).read()
        regex_country_code = '<countryCode>(.*?)</countryCode>'
        country_code = findall(regex_country_code, xml_data)[0]
        return country_code.lower()
    except: return language