import os

from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class SerialConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = yield self.connection[device.servername]
        self.context = yield self.server.context()
        self.ID = self.server.ID

        yield self.server.open(device.address)
        
        for attr in ['timeout', 'baudrate', 'stopbits', 'bytesize']:
            if hasattr(device, attr): 
                value = getattr(device, attr)
                yield getattr(self.server, attr)(value)
    
    @inlineCallbacks
    def baudrate(self, x=None):
        yield self.server.baudrate(x)
   
    @inlineCallbacks
    def timeout(self, x=None):
        yield self.server.timeout(x)
    
    @inlineCallbacks
    def write(self, x):
        yield self.server.write(x)

    @inlineCallbacks
    def write_line(self, x):
        yield self.server.write_line(x)
    
    @inlineCallbacks
    def write_lines(self, x):
        yield self.server.write_lines(x)
    
    @inlineCallbacks
    def read(self, x=0):
        ans = yield self.server.read(x)
        returnValue(ans)
    
    @inlineCallbacks
    def read_line(self):
        ans = yield self.server.read_line()
        returnValue(ans)

    @inlineCallbacks
    def read_lines(self):
        ans = yield self.server.read()
        returnValue(ans)

    @inlineCallbacks
    def close(self):
        yield self.server.close()
    
    @inlineCallbacks
    def flushinput(self):
        yield self.server.flushinput()
    
    @inlineCallbacks
    def flushoutput(self):
        yield self.server.flushoutput()
