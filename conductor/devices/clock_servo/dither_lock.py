import sys
from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

sys.path.append('../')
from generic_device.generic_parameter import GenericParameter
from lib.pid import Dither, DitherPIID

class DitherLock(GenericParameter):
    priority = 9
    def __init__(self, config):
        super(DitherLock, self).__init__(config)
        self.pid = {lock_name: DitherPIID(**lock_conf['pid']) 
            for lock_name, lock_conf in config.items()}
        self.dither = {lock_name: Dither(**lock_conf['dither']) 
            for lock_name, lock_conf in config.items()}
        self._value = {}

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()

    @inlineCallbacks
    def update(self):
        """ sefl.value == {
            'dither': [dither_name, side],
            'pid': [pid_name, side],
        }
        """
        dither_value = self.value.get('dither')
        if dither_value:
            name = dither_value[0]
            side = dither_value[1]
            center = self.pid[name].output
            out = self.dither[name].tick(dither_side, dither_center)
            clock_aom_value = {'clock_aom': {'frequency': out}}
            yield self.set_parameter_values(json.dumps(clock_aom_value))

        pid_value = self.value.get('pid')
        if pid_value:
            name = pid_value[0]
            side = pid_value[1]
            data = yield self.cxn.get_data()
            frac = data['gage']['frac'][-1]
            out = self.pid[name].tick(side, frac)
            pid_value = {name: {'frequency': out}}
            yield self.set_parameter_values(json.dumps(pid_value))
