import json
import logging
import xbmc
import time
import requests

from random import randint
from threading import Thread, Event
from urlparse import urljoin


log = logging.getLogger(__name__)


class UHSClient(object):
    """
    API Client, reverse engineered by observing the interactions
    between the web browser and the ustream servers.
    """
    API_URL = "http://r{0}-1-{1}-{2}-{3}.ums.ustream.tv"
    APP_ID, APP_VERSION = 11, 2
    USER_AGENT = ("Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) "
                  "AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 "
                  "Mobile/10A5376e Safari/8536.25")

    def __init__(self, media_id, application, **options):
        self.media_id = media_id
        self.application = application
        self.referrer = options.pop("referrer", None)
        self._host = None
        self.rsid = self.generate_rsid()
        self.rpin = self.generate_rpin()
        self._connection_id = options.pop("connection_id", None)
        self._app_id = options.pop("app_id", self.APP_ID)
        self._app_version = options.pop("app_version", self.APP_VERSION)
        self._cluster = options.pop("cluster", "live")
        self._password = options.pop("password", None)

    def connect(self, **options):
        raw = self.send_command(type="viewer", appId=self._app_id,
                                appVersion=self._app_version,
                                rsid=self.rsid,
                                rpin=self.rpin,
                                referrer=self.referrer,
                                media=str(self.media_id),
                                application=self.application,
                                password=self._password)
        result = raw[0]["args"][0]
        self._host = "http://{0}".format(result["host"])
        self._connection_id = result["connectionId"]
        xbmc.log("Got new host={0}, and connectionId={1}".format(self._host, self._connection_id), xbmc.LOGDEBUG)
        return True

    def poll(self, schema=None, retries=5, timeout=5.0):
        stime = time.time()
        try:
            r = self.send_command(connectionId=self._connection_id,
                                  schema=schema,
                                  retries=retries,
                                  timeout=timeout)
        except Exception as err:
            xbmc.log("poll took {0:.2f}s: {1}".format(time.time() - stime, err), xbmc.LOGDEBUG)
        else:
            xbmc.log("poll took {0:.2f}s".format(time.time() - stime), xbmc.LOGDEBUG)
            return r

    @staticmethod
    def generate_rsid():
        return "{0:x}:{1:x}".format(randint(0, 1e10), randint(0, 1e10))

    @staticmethod
    def generate_rpin():
        return "_rpin.{0}".format(randint(0, 1e15))

    def send_command(self, timeout=5.0, **args):
        res = requests.get(self.host,
                           params=args,
                           headers={"Referer": self.referrer,
                                    "User-Agent": self.USER_AGENT},
                           timeout=timeout)
        return json.loads(res.text)

    @property
    def host(self):
        host = self._host or self.API_URL.format(randint(0, 0xffffff), self.media_id, self.application,
                                                 "lp-" + self._cluster)
        return urljoin(host, "/1/ustream")


class UStreamPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)
        self._poller = None
        self.api = None
        self.playbackEnded = False
        self.interval = 10

    def playChannel(self, channel_id):
        streams = list(self._api_get_streams(channel_id, "channel"))
        self.play(streams[0])
        i = 0
        while i < 20 or self.isPlaying():
            xbmc.sleep(250)
            i += 1

    def _api_get_streams(self, media_id, application, cluster="live", referrer=None, retries=3):
        if retries > 0:
            app_id = 11
            app_ver = 2
            referrer = referrer or ""
            self.api = UHSClient(media_id, application, referrer=referrer, cluster=cluster, app_id=app_id,
                                 app_version=app_ver)
            xbmc.log("Connecting to UStream API: media_id={0}, application={1}, referrer={2}, cluster={3}, "
                     "app_id={4}, app_ver={5}".format(media_id, application, referrer, cluster, app_id, app_ver),
                     xbmc.LOGDEBUG)
            if self.api.connect():
                for i in range(5):  # make at most five requests to get the moduleInfo
                    try:
                        for s in self._do_poll(media_id, application, cluster, referrer, retries):
                            yield s
                    except ValueError:
                        xbmc.log("Retrying moduleInfo request", xbmc.LOGDEBUG)
                        time.sleep(1)
                    else:
                        break

    def _do_poll(self, media_id, application, cluster="live", referrer=None, retries=3):
        res = self.api.poll()
        if res:
            for result in res:
                if result["cmd"] == "moduleInfo":
                    for s in self.handle_module_info(result["args"], media_id, application, cluster,
                                                     referrer, retries):
                        yield s
                elif result["cmd"] == "reject":
                    for s in self.handle_reject(result["args"], media_id, application, cluster, referrer, retries):
                        yield s
                else:
                    xbmc.log("Unknown command: {0}({1})".format(result["cmd"], result["args"]), xbmc.LOGDEBUG)

    def handle_module_info(self, args, media_id, application, cluster="live", referrer=None, retries=3):
        has_results = False
        for arg in args:
            streams = arg.get("stream")
            if streams:
                has_results = True
                if isinstance(streams, list):
                    for stream in streams:
                        yield stream["url"]
                elif isinstance(streams, dict):
                    for stream in streams.get("streams", []):
                        for surl in stream["streamName"]:
                            yield surl
                elif streams == "offline":
                    xbmc.log("This stream is currently offline", xbmc.LOGWARNING)

        if not has_results:
            raise ValueError

    def handle_reject(self, args, media_id, application, cluster="live", referrer=None, retries=3):
        for arg in args:
            if "cluster" in arg:
                xbmc.log("Switching cluster to {0}".format(arg["cluster"]["name"]), xbmc.LOGDEBUG)
                cluster = arg["cluster"]["name"]
            if "referrerLock" in arg:
                referrer = arg["referrerLock"]["redirectUrl"]

        return self._api_get_streams(media_id,
                                     application,
                                     cluster=cluster,
                                     referrer=referrer,
                                     retries=retries - 1)



    def onPlayBackStarted(self):
        xbmc.log(">> polling started")

        while self.isPlaying():
            res = self.api.poll(retries=30, timeout=self.interval)
            if not res:
                continue
            for cmd_args in res:
                xbmc.log("poll response: {0}".format(cmd_args), xbmc.LOGDEBUG)
                if cmd_args["cmd"] == "warning":
                    xbmc.log("{code}: {message}".format(**cmd_args["args"]), xbmc.LOGDEBUG)

        xbmc.log(">> polling ended")
