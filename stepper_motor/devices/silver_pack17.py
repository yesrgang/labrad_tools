import labrad.types as T

from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceWrapper

class SilverPack17(DeviceWrapper):
    def __init__(self, config):
        self.timeout = .5
        
        self.init_commands = [
            '/1m30h10R\r' # current
            '/1V1000L500R\r' # velocity and acceleration
            '/1j256o1500R\r' # step resolution
        ]
        
        for key, value in config.items():
            setattr(self, key, value)
   
        super(SilverPack17, self).__init__({})

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

    @inlineCallbacks
    def toggle_absolute(self,position1,position2):
        command = '/1s0gH04A{}H14A{}G0R\r'.format(position1,position2)
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        yield self.connection.write('/1e0R\r')
        ans = yield self.connection.read_line()
        print ans
        

