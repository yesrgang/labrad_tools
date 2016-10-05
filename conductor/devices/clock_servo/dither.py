import sys
sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync


class Dither(GenericParameter):
