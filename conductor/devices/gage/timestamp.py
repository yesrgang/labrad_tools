import sys
import time

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

sys.path.append('../')
from generic_device.generic_parameter import GenericParameter


class Timestamp(GenericParameter):
    def value(self):
        return time.time()


        
