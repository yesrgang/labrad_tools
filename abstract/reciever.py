import json

import ok
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from okfpga.sequencer.sequence import Sequence

class ReceiverServer(LabradServer):
    name = '%LABRADNODE% Receiver'
    
    @setting(1, 'send string', string='s', returns='s')
    def load_sequence(self, c, string):
        print string
        return string


if __name__ == "__main__":
    __server__ = ReceiverServer()
    from labrad import util
    util.runServer(__server__)
