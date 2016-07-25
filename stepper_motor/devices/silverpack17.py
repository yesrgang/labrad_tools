import labrad.types as T

from twisted.internet.defer import inlineCallbacks, returnValue

class SilverPack17(object):
    def __init__(self, config):
        self.timeout = T.Value(1, 's')
        self.baudrate = 9600
        self.stopbits=1
        self.bytesize=8
        
        self.init_commands = [
            '/1m30h10R\r' # current
            '/1V1000L500R\r' # velocity and acceleration
            '/1j256o1500R\r' # step resolution
        ]
        
        for key, value in config.items():
            setattr(self, key, value)
   
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.connection.write(command)
            ans = yield self.connection.read_line()
    
    @inlineCallbacks
    def move_absolute(self, position):
        command = '/1A{}R\r'.format(position)
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        self.position = position