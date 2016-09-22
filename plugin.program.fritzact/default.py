#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Documentation for the login procedure
http://www.avm.de/de/Extern/files/session_id/AVM_Technical_Note_-_Session_ID.pdf

Smart Home interface:
https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA-HTTP-Interface.pdf
'''

import hashlib
import os
import requests
import resources.lib.tools as t
import sys
from time import time
import urllib
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from xml.etree import ElementTree as ET

__addon__ = xbmcaddon.Addon()
__addonID__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__path__ = __addon__.getAddonInfo('path')
__LS__ = __addon__.getLocalizedString

__on__ = xbmc.translatePath(os.path.join(__path__, 'resources', 'lib', 'media', 'dect_on.png'))
__off__ = xbmc.translatePath(os.path.join(__path__, 'resources', 'lib', 'media', 'dect_off.png'))
__absent__ = xbmc.translatePath(os.path.join(__path__, 'resources', 'lib', 'media', 'dect_absent.png'))

class Device():

    def __init__(self, device):

        # Device attributes

        self.actor_id = device.attrib['identifier']
        self.device_id = device.attrib['id']
        self.fwversion = device.attrib['fwversion']
        self.productname = device.attrib['productname']
        self.manufacturer = device.attrib['manufacturer']
        self.functionbitmask = int(device.attrib['functionbitmask'])

        self.name = device.find('name').text
        self.present = int(device.find('present').text or '0')
        self.b_present = 'true' if self.present == 1 else 'false'

        self.is_thermostat = self.functionbitmask & (1 << 6) > 0        # Comet DECT (Radiator Thermostat)
        self.has_powermeter = self.functionbitmask & (1 << 7) > 0       # Energy Sensor
        self.has_temperature = self.functionbitmask & (1 << 8) > 0      # Temperature Sensor
        self.is_switch = self.functionbitmask & (1 << 9) > 0            # Power Switch
        self.is_repeater = self.functionbitmask & (1 << 10) > 0         # DECT Repeater

        # Switch attributes

        if self.is_switch:
            self.state = int(device.find('switch').find('state').text or '0')
            self.b_state = 'true' if self.state == 1 else 'false'
            self.mode = device.find('switch').find('mode').text
            self.lock = int(device.find('switch').find('lock').text or '0')

        # Power attributes

        if self.has_powermeter:
            self.power = 0.0
            self.energy = 0.0
            self.power = '{:0.2f}'.format(float(device.find('powermeter').find('power').text)/1000)
            self.energy = '{:0.2f}'.format(float(device.find('powermeter').find('energy').text)/1000)

        # Temperature attributes

        if self.has_temperature:
            self.temperature = 0.0
            self.temperature = '{:0.1f}'.format(float(device.find("temperature").find("celsius").text)/10)

class FritzBox():

    def __init__(self):
        self.getSettings()
        self.base_url = self.__fbtls + self.__fbserver

        self.session = requests.Session()

        if self.__fbSID is None or (int(time()) - self.__lastLogin > 600):

            t.writeLog('SID is none/last login more than 10 minutes ago, try to login')
            sid = None

            try:
                response = self.session.get(self.base_url + '/login_sid.lua', verify=False)
                xml = ET.fromstring(response.text)
                if xml.find('SID').text == "0000000000000000":
                    challenge = xml.find('Challenge').text
                    url = self.base_url + '/login_sid.lua'
                    response = self.session.get(url, params={
                        "username": self.__fbuser,
                        "response": self.calculate_response(challenge, self.__fbpasswd),
                    }, verify=False)
                    xml = ET.fromstring(response.text)
                    if xml.find('SID').text == "0000000000000000":
                        blocktime = int(xml.find('BlockTime').text)
                        t.writeLog("Login failed, please wait %s seconds" % (blocktime), xbmc.LOGERROR)
                        t.notifyOSD(__addonname__, __LS__(30012))
                    else:
                        sid = xml.find('SID').text

            except (requests.exceptions.ConnectionError, TypeError) as e:
                t.writeLog('FritzBox unreachable', level=xbmc.LOGERROR)
                t.notifyOSD(__addonname__, __LS__(30010))

            self.__fbSID = sid
            self.__lastLogin = int(time())
            __addon__.setSetting('SID', self.__fbSID)
            __addon__.setSetting('lastLogin', str(self.__lastLogin))

    def calculate_response(self, challenge, password):

        # Calculate response for the challenge-response authentication

        to_hash = (challenge + "-" + password).encode("UTF-16LE")
        hashed = hashlib.md5(to_hash).hexdigest()
        return '%s-%s' % (challenge, hashed)

    def getSettings(self):
        self.__fbserver = __addon__.getSetting('fbServer')
        self.__fbuser = __addon__.getSetting('fbUser')
        self.__fbpasswd = t.crypt('fbPasswd', 'fb_key', 'fb_token')
        self.__fbtls = 'https://' if __addon__.getSetting('fbTLS').upper() == 'TRUE' else 'http://'
        self.__prefAIN = __addon__.getSetting('preferredAIN')
        #
        self.__lastLogin = int(__addon__.getSetting('lastLogin') or 0)
        self.__fbSID = __addon__.getSetting('SID') or None

    def get_actors(self, handle=None):

        # Returns a list of Actor objects for querying SmartHome devices.

        devices = self.switch("getdevicelistinfos")
        if devices is not None:
            actors = []
            for device in ET.fromstring(devices):
                #
                # TEST WITH MORE THEN ONE DEVICE CHANGE RANGE
                #
                for d in range(1):
                    actor = Device(device)

                    actor.icon = __absent__
                    if actor.present == 1:
                        actor.icon = __on__
                        if actor.state == 0: actor.icon = __off__

                    actors.append(actor)

                    if handle is not None:
                        wid = xbmcgui.ListItem(label=actor.name, label2=actor.actor_id, iconImage=actor.icon)
                        wid.setProperty('present', __LS__(30032 + actor.present))
                        wid.setProperty('b_present', actor.b_present)
                        wid.setProperty('state', __LS__(30030 + actor.state))
                        wid.setProperty('b_state', actor.b_state)
                        wid.setProperty('mode', actor.mode)
                        wid.setProperty('temperature', str(actor.temperature))
                        wid.setProperty('power', actor.power)
                        wid.setProperty('energy', actor.energy)
                        xbmcplugin.addDirectoryItem(handle=handle, url='', listitem=wid)

            if handle is not None:
                xbmcplugin.endOfDirectory(handle=handle, updateListing=True)
            xbmc.executebuiltin('Container.Refresh')
            return actors

    def switch(self, cmd, ain=None):

        # Call an actor method

        if self.__fbSID is None:
            t.writeLog('Not logged in', level=xbmc.LOGERROR)
            return

        params = {
            'switchcmd': cmd,
            'sid': self.__fbSID,
        }
        if ain: params['ain'] = ain
        response = self.session.get(self.base_url + '/webservices/homeautoswitch.lua', params=params, verify=False)
        response.raise_for_status()
        return response.text.strip()

# _______________________________
#
#           M A I N
# _______________________________

action = None
ain = None
_addonHandle = None

fritz = FritzBox()

arguments = sys.argv

if len(arguments) > 1:
    if arguments[0][0:6] == 'plugin':
        _addonHandle = int(arguments[1])
        arguments.pop(0)
        arguments[1] = arguments[1][1:]
        t.writeLog('calling script as plugin source (handle #%s)' % (_addonHandle), level=xbmc.LOGDEBUG)

    params = t.paramsToDict(arguments[1])
    action = urllib.unquote_plus(params.get('action', ''))
    ain = urllib.unquote_plus(params.get('ain', ''))

    t.writeLog('provided parameter hash: %s' % (arguments[1]), level=xbmc.LOGDEBUG)

    if action is not None:
        if action == 'toggle':
            fritz.switch('setswitchtoggle', ain)
            xbmcgui.Window(10000).setProperty('fritzact.timestamp', str(int(time())))

        elif action == 'on':
            fritz.switch('setswitchon', ain)
            xbmcgui.Window(10000).setProperty('fritzact.timestamp', str(int(time())))

        elif action == 'off':
            fritz.switch('setswitchoff', ain)
            xbmcgui.Window(10000).setProperty('fritzact.timestamp', str(int(time())))

else:
    if __addon__.getSetting('preferredAIN') is not None:
        fritz.switch('setswitchtoggle', __addon__.getSetting('preferredAIN'))
        xbmcgui.Window(10000).setProperty('fritzact.timestamp', str(int(time())))

actors = fritz.get_actors(handle=_addonHandle)
if actors is not None:
    for device in actors:
        t.writeLog('-------------------------------------', level=xbmc.LOGDEBUG)
        t.writeLog('Name:        %s' % (device.name), level=xbmc.LOGDEBUG)
        t.writeLog('ID (AIN):    %s' % (device.actor_id), level=xbmc.LOGDEBUG)
        t.writeLog('Presence:    %s' % (device.present), level=xbmc.LOGDEBUG)
        t.writeLog('Device ID:   %s' % (device.device_id), level=xbmc.LOGDEBUG)
        t.writeLog('Temperature: %s °C'.decode('utf-8') % (device.temperature), level=xbmc.LOGDEBUG)
        t.writeLog('State:       %s' % (device.state), level=xbmc.LOGDEBUG)
        t.writeLog('Power:       %s W' % (device.power), level=xbmc.LOGDEBUG)
        t.writeLog('Consumption: %s kWh' % (device.energy), level=xbmc.LOGDEBUG)
