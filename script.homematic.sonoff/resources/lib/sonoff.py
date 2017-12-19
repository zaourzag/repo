#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import re
import sys

class Sonoff_Switch(object):

    TIMEOUT = 3
    SONOFF_CGI = '/cm'
    STATUS = {'cmnd': 'Power Status'}
    TOGGLE = {'cmnd': 'Power Toggle'}
    ON = {'cmnd': 'Power On'}
    OFF = {'cmnd': 'Power Off'}


    @classmethod
    def select_ip(cls, device):
        return unicode(re.findall(r'[0-9]+(?:\.[0-9]+){3}', device)[0])

    def get_devices(self, devices):
        '''

        :param devices: device list
        :return: dict {device: status (ON|OFF|UNREACHABLE|UNDEFINED}
        '''
        dl = {}
        for d in devices:
            device = self.select_ip(d)
            dl.update({device: self.send_command(device, self.STATUS)})
        return dl

    def send_command(self, device, command):
        device = self.select_ip(device)
        try:
            req = requests.get('http://%s%s' % (device, self.SONOFF_CGI), command, timeout=self.TIMEOUT)
            req.raise_for_status()
            response = req.text.splitlines()
            for r in response:
                if ' = ' in r:
                    key, val = r.split(' = ')
                    if key == 'RESULT': return json.loads(val, encoding=req.encoding)['POWER']
        except requests.ConnectionError:
            return u'UNREACHABLE'
        except requests.HTTPError:
            return u'UNDEFINED'
        except Exception, e:
            print e.message


if __name__ == '__main__':
    sd = Sonoff_Switch()
    print sd.send_command(sys.argv[1], sd.TOGGLE)
