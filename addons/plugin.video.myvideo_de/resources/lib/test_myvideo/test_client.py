from resources.lib.myvideo import Client

__author__ = 'L0RE'

import unittest


class TestClient(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_format(self):
        client = Client()
        json_data = client.get_format('752901')
        pass

    def test_get_video_url(self):
        client = Client()
        json_data = client.get_video_url('11299598')
        video_url = json_data['VideoURL']

        self.assertTrue(video_url.startswith('http://myvideo'))
        pass

    def test_search(self):
        client = Client()
        json_data = client.search('halligalli')
        screen = json_data['screen']
        pass

    def test_get_screen(self):
        client = Client()
        json_data = client.get_screen(screen_id=10)
        screen_objects = json_data['screen']['screen_objects']
        for screen_object in screen_objects:
            screen_object_type = screen_object['type']
            if screen_object_type != 'home_header':
                title = screen_object['title']
                print title
                pass
            pass
        pass

    def test_get_home(self):
        client = Client()
        json_data = client.get_home()

        # if the result has changed this should crash
        menu_items = json_data['menubar']['channels'][0]['menu_items']

        for menu_item in menu_items:
            title = menu_item['displayName']
            print title
            pass
        pass

    pass
