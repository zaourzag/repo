__author__ = 'L0RE'

try:
    from .impl.xbmc.xbmc_input import *
except ImportError:
    from .impl.mock.mock_input import *
    pass
