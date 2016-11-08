from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceWrapper

class AG53132A(DeviceWrapper):
    @inlineCallbacks
    def initialize(self):
#        yield self.connection.write('*RST')
#        yield self.connection.write('*CLS')
        yield self.connection.write(":FUNC 'FREQ 1'")
        yield self.connection.write(":FREQ:ARM:STAR:SOUR EXT")
        yield self.connection.write(":FREQ:ARM:STOP:SOUR EXT")
        yield self.connection.write("INIT:CONT ON")
        yield self.connection.timeout(30000)

    @inlineCallbacks
    def get_frequency(self):
        response = yield self.connection.query('FETCH:FREQ?')
        returnValue(float(response))
