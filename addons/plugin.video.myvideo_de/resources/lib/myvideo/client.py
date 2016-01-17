import requests

__author__ = 'L0RE'


class Client(object):
    def __init__(self):
        pass

    def get_format(self, format_id):
        return self._perform_request(path='/myvideo-app/v1/tablet/format/show/%s' % format_id)

    def get_video_url(self, video_id):
        return self._perform_request(
            path='/myvideo-app/v1/vas/video.json?clipid=%s&app=megapp&method=4' % str(video_id))

    def search(self, query):
        return self._perform_request(path='/myvideo-app/v1/tablet/search?query=%s' % query)

    def get_screen(self, screen_id):
        return self._perform_request(path='/myvideo-app/v1/tablet/screen/%s' % screen_id)

    def get_home(self):
        return self._perform_request(path='/static/myvideo.json')

    def _perform_request(self, method='GET', headers=None, path=None, post_data=None, params=None,
                         allow_redirects=True):
        # params
        if not params:
            params = {}
            pass
        _params = {}
        _params.update(params)

        # headers
        if not headers:
            headers = {}
            pass

        _headers = {'Accept-Language': 'en_US',
                    'X-PAPI-AUTH': '39927b3f31d7c423ad6f862e63d8436d954aecd0',
                    'Host': 'papi.myvideo.de',
                    'Connection': 'Keep-Alive',
                    'User-Agent': 'Not set yet'}
        _headers.update(headers)

        # url
        _url = 'https://papi.myvideo.de/%s' % path.strip('/')

        result = None
        if method == 'GET':
            result = requests.get(_url, params=_params, headers=_headers, verify=False, allow_redirects=allow_redirects)
        elif method == 'POST':
            result = requests.post(_url, data=post_data, params=_params, headers=_headers, verify=False,
                                   allow_redirects=allow_redirects)

        if result is None:
            return {}

        return result.json()

    pass
