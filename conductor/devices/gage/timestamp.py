import sys
import time

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

sys.path.append('../')
from generic_device.generic_parameter import GenericParameter


class Timestamp(GenericParameter):
    value_type = 'read'
    priority = 1

    @inlineCallbacks
    def update(self):
        yield None
        self._value = time.time()

    @property
    def value(self):
#        if not self._value:
#            self._value = time.time()
        return self._value

    @value.setter
    def value(self, value):
        pass


        
