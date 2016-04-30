from resources.lib import kodimon
from resources.lib.myvideo import Provider

__author__ = 'L0RE'

import unittest


class TestProvider(unittest.TestCase):
    def setUp(self):
        pass

    def test_format(self):
        provider = Provider()

        result = provider.navigate('/format/752901/')
        items = result[0]

        kodimon.print_items(items)
        pass

    def test_search(self):
        provider = Provider()

        path = '/%s/query/' % provider.PATH_SEARCH
        result = provider.navigate(path, {'q': 'halligalli'})
        items = result[0]

        kodimon.print_items(items)
        pass

    def test_on_sub_screen(self):
        provider = Provider()
        result = provider.navigate('/screen/30/Top Serien/')
        items = result[0]

        kodimon.print_items(items)
        pass

    def test_on_screen(self):
        provider = Provider()
        result = provider.navigate('/screen/50/')
        items = result[0]

        kodimon.print_items(items)
        pass

    def test_on_root(self):
        provider = Provider()
        result = provider.navigate('/')
        items = result[0]

        kodimon.print_items(items)
        pass
    pass
