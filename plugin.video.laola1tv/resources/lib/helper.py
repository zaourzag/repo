# -*- coding: utf-8 -*-

from common import *

def unas_url(data):
    if data.get('status', 'error') == 'success':
        return data['data']['stream-access'][0]
    else:
        message = data.get('message', 'error')
        dialog.ok(addon_name, utfenc(message))

def user(data):
    if data.get('error', None):
        return data['error'][0]
    elif data.get('result', None):
        return 'login=success country=%s premium=%s' % (data['result']['country'], data['result']['premium'])
    else:
        return 'error'

def master(data):
    a = re.search('auth="(.*?)"', data)
    b = re.search('url="(http.*?)"', data)
    c = re.search('comment="(.*?)"', data)
    if a and b:
        return '%s?hdnea=%s' % (b.group(1), a.group(1))
    elif c:
        dialog.ok('Laola1 TV', utfenc(c.group(1)))

def create_cookie(data):
    cookie = ''
    premium = re.search('premium=(.*?);', data)
    email   = re.search('email=(.*?);', data)
    session = re.search('session=(.*?);', data)
    if premium and email and session:
        cookie = 'premium=%s; email=%s; session=%s' % (premium.group(1),email.group(1),session.group(1))
    return cookie