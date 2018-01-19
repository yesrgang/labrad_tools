from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceWrapper

class SilverPack17(DeviceWrapper):
    serial_server_name = None
    serial_address = None
    timeout = 0.5
    init_commands = [
        '/1m30h10R\r' # current
        '/1V1000L500R\r' # velocity and acceleration
        '/1j256o1500R\r' # step resolution
        ]

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)

        for command in self.init_commands:
            yield self.serial_server.write(command)
            ans = yield self.serial_server.read_line()
    
    @inlineCallbacks
    def move_absolute(self, position):
        command = '/1A{}R\r'.format(position)
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        self.position = position

    @inlineCallbacks
    def toggle_absolute(self,position1,position2):
        command = '/1s0gH04A{}H14A{}G0R\r'.format(position1,position2)
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        yield self.serial_server.write('/1e0R\r')
        ans = yield self.serial_server.read_line()
