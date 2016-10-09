import sys
sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from lib.helpers import get_measurements

class Tot(GenericParameter):
    value_type = 'read'

    @inlineCallbacks
    def update(self, value):
        yield None
        self._value = None

    @property
    def value(self):
        if not self._value:
            self._value = get_measurements()['tot']
        return self._value

    @value.setter
    def value(self, value):
        pass

