import os

from twisted.internet.defer import inlineCallbacks
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

    def baudrate(self, x):
        self.server.baudrate(x)
        
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
        return self.server.read_lines()

    def close(self):
        return self.server.close()

    def flushinput(self):
        return self.server.flushinput()

    def flushoutput(self):
        return self.server.flushoutput()
#        self.write = lambda s: server.write(s)
#        self.write_line = lambda s: server.write_line(s)
#        self.write_lines = lambda s: server.write_lines(s)
#        self.read = lambda x = 0: server.read(x)
#        self.read_line = lambda: server.read_line()
#        self.read_lines = lambda: server.read_lines()
#        self.close = lambda: server.close()
#        self.flushinput = lambda: server.flushinput()
#        self.flushoutput = lambda: server.flushoutput()
#        self.ID = server.ID
