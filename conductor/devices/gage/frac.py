import sys
sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from lib.helpers import get_measurements

class Frac(GenericParameter):
    value_type = 'read'
    priority = 1

    @inlineCallbacks
    def update(self):
        yield None
        self._value = None

    @property
    def value(self):
#        if not self._value:
#            self._value = get_measurements()['frac']
        self._value = get_measurements()['frac']
        return self._value

    @value.setter
    def value(self, value):
        pass

