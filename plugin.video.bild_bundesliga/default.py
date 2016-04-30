# -*- coding: utf-8 -*-
import sys

params = dict(part.split('=') for part in sys.argv[2][1:].split('&') if len(part.split('=')) == 2)
lib = params.get('lib', 'index')
function = params.get('function', 'index')
arg = params.get('arg', '')

exec 'from resources.lib.%s import %s' % (lib, function)
exec '%s(arg)' % function