#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import re
import sys

class Sonoff_Switch(object):

    TIMEOUT = 3
    SONOFF_CGI = '/cm'
    STATUS = [{'cmnd': 'Power Status'}, {'cmnd': 'Power2 Status'}, {'cmnd': 'Power3 Status'}, {'cmnd': 'Power4 Status'}]
    TOGGLE = [{'cmnd': 'Power Toggle'}, {'cmnd': 'Power2 Toggle'}, {'cmnd': 'Power3 Toggle'}, {'cmnd': 'Power4 Toggle'}]
    ON = [{'cmnd': 'Power On'}, {'cmnd': 'Power2 On'}, {'cmnd': 'Power3 On'}, {'cmnd': 'Power4 On'}]
    OFF = [{'cmnd': 'Power Off'}, {'cmnd': 'Power2 Off'}, {'cmnd': 'Power3 Off'}, {'cmnd': 'Power4 Off'}]


    @classmethod
    def select_ip(cls, device):
        return unicode(re.findall(r'[0-9]+(?:\.[0-9]+){3}', device)[0])

    def send_command(self, device, command, channel=''):
        device = self.select_ip(device)
        try:
            req = requests.get('http://%s%s' % (device, self.SONOFF_CGI), command, timeout=self.TIMEOUT)
            req.raise_for_status()
            response = req.text.splitlines()
            for r in response:
                if ' = ' in r:
                    key, val = r.split(' = ')
                    if key == 'RESULT': return json.loads(val, encoding=req.encoding)['POWER%s' % (channel)]
        except requests.ConnectionError:
            return u'UNREACHABLE'
        except requests.HTTPError:
            return u'UNDEFINED'
        except Exception, e:
            print e.message


if __name__ == '__main__':
    sd = Sonoff_Switch()
    print sd.send_command(sys.argv[1], sd.TOGGLE)
