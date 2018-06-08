from twisted.internet.defer import Deferred
from twisted.internet.reactor import callLater

def deferred_sleep(secs):
    d = Deferred()
    callLater(secs, d.callback, None)
    return d
