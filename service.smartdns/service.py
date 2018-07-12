# coding=utf-8
#
#
# 	 smartdns
# 	(c) 2017 Steffen Rolapp

#

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, re, base64
import urllib, urllib2

__addon__ = xbmcaddon.Addon()
__addonId__=__addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')

URL = __addon__.getSetting('dnsurl')
if URL == '':
	__addon__.openSettings()
	URL = __addon__.getSetting('dnsurl')
	
TESTIP = 'http://ifconfig.co/ip'
OLDIP = "0"

def testip(IP):
    OLDIP = IP
    try:
        handle = urllib2.urlopen(TESTIP)
        newip = handle.read()
    except:
        newip = OLDIP
   
    if  OLDIP != newip:
		
		OLDIP = newip
		handle = urllib2.urlopen(URL)	
		html = handle.read()
        #html = 'test'
		xbmcgui.Dialog().notification('SmartDNS', str(html) + " " + str(newip),   __addon__.getAddonInfo('path') + '/icon.jpg', 3000, False)
    return OLDIP
        
def timer(OLDIP):
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(300): break
        OLDIP = testip(OLDIP)
        #print 'OLDIP ' + str(OLDIP)
	
OLDIP = testip(OLDIP)
timer(OLDIP)
