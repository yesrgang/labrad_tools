from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device

class SilverPack17(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.5

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)

        # set current
        yield self.serial_server.write('/1m30h10R\r')
        ans = yield self.serial_server.read_line()

        # set velocity and acceleration
        yield self.serial_server.write('/1V1000L500R\r')
        ans = yield self.serial_server.read_line()

        # set step resolution
        yield self.serial_server.write('/1j256o1500R\r')
        ans = yield self.serial_server.read_line()
    
    @inlineCallbacks
    def move_absolute(self, position):
        command = '/1A{}R\r'.format(position)
        print command
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        self.position = position

    @inlineCallbacks
    def toggle_absolute(self,position1, position2):
        command = '/1gH04A{}H14A{}G0R\r'.format(position1, position2)
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
#        command = '/1s0gH04A{}H14A{}G0R\r'.format(position1, position2)
#        yield self.serial_server.write(command)
#        ans = yield self.serial_server.read_line()
#        yield self.serial_server.write('/1e0R\r')
#        ans = yield self.serial_server.read_line()
