from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceWrapper

class AG53220A(DeviceWrapper):
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        command = 'MEAS:FREQ? DEF, DEF, (@{})'.format(self.counter_source)
        response = yield self.connection.query(command)
        returnValue(float(response))
