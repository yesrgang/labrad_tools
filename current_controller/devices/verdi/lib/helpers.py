from datetime import datetime

from twisted.internet.defer import Deferred
from twisted.internet.reactor import callLater

def seconds_til_start(delta_day, hour):
    now = datetime.now()
    start = now.replace(day=now.day+delta_day, hour=hour, minute=0, second=0, 
                        microsecond=0)
    if now > start:
        raise Exception('start time is in the past')
    return (start-now).seconds

def cancel_delayed_calls(device):
    for call in device.delayed_calls:
        if call.active():
            call.cancel()
    device.delayed_calls = []

def sleep(secs):
    d = Deferred()
    callLater(secs, d.callback, None)
    return d
