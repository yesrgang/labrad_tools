import os

from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class SerialConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = yield self.connection[device.servername]
        self.context = self.server.context()
        self.ID = self.server.ID

        self.server.open(device.address)
        
        for attr in ['timeout', 'baudrate', 'stopbits', 'bytesize']:
            if hasattr(device, attr): 
                value = getattr(device, attr)
                getattr(self.server, attr)(value)

    def baudrate(self, x=None):
        return self.server.baudrate(x)
    
    def timeout(self, x=None):
        return self.server.timeout(x)
        
    def write(self, x):
        return self.server.write(x)

    def write_line(self, x):
        return self.server.write_line(x)

    def write_lines(self, x):
        return self.server.write_lines(x)

    def read(self, x=0):
        return self.server.read(x)

    def read_line(self):
        return self.server.read_line()

    def read_lines(self):
        return self.server.read()

    def close(self):
        return self.server.close()

    def flushinput(self):
        return self.server.flushinput()

    def flushoutput(self):
        return self.server.flushoutput()
