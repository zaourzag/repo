from resources.lib import kodimon
from resources.lib import myvideo

__provider__ = myvideo.Provider()
kodimon.run(__provider__)