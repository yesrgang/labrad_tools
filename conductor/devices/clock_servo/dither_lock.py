import json
from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter
from lib.pid import Dither, DitherPIID

from lib.get_frac import get_frac

class DitherLock(ConductorParameter):
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
        yield self.connect()

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

            out = self.dither[name].tick(side, center)
            yield self.conductor.set_parameter_value('clock_aom', 'frequency', out)

        pid_value = self.value.get('pid')
        if pid_value:
            name = pid_value[0]
            side = pid_value[1]
            readout_device = self.pid[name].readout_device
            data = self.conductor.data.get(readout_device)
            frac = get_frac(readout_device, data)

            if frac:
                out = self.pid[name].tick(side, frac)
                yield self.conductor.set_parameter_value(name, 'frequency', out, True)
