from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from lib.pid import Dither, DitherPIID

class DitherLock(object):
    pid = {}
    def __init__(self):
        self.priority = 9
        self.value_type = 'single'
        self.value = {}

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
    
    @inlineCallbacks
    def stop(self):
        yield None

    @inlineCallbacks
    def update(self, value):
        """ value = {
            'dither': [dither_name, side],
            'pid': [pid_name, side],
        }
        """
        print 'pids', self.pid.keys()
        print value
        dither_value = value.get('dither')
        if dither_value:
            name = dither_value[0]
            side = dither_value[1]
            center = self.pid[name].output
            out = self.dither[name].tick(dither_side, dither_center)
            clock_aom_value = {'clock_aom': {'frequency': out}}
            yield self.set_parameter_values(json.dumps(clock_aom_value))

        pid_value = value.get('pid')
        if pid_value:
            name = pid_value[0]
            side = pid_value[1]
            data = yield self.cxn.get_data()
            frac = data['gage']['frac'][-1]
            out = self.pid[name].tick(side, frac)
            pid_value = {name: {'frequency': out}}
            yield self.set_parameter_values(json.dumps(pid_value))


def dither_lock_maker(config):
    dither_lock = DitherLock
    pid = {}
    dither = {}
    for lock_name, lock_config in config.items():
        dither[lock_name] = Dither(**lock_config['dither'])
        pid[lock_name] = DitherPIID(**lock_config['pid'])
    dither_lock.pid = pid
    dither_lock.dither = dither
    return dither_lock()
