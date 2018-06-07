from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device

class AFG3252(Device):
    visa_server_name = None
    visa_address = None

    source = None
    
    frequency = None
    frequency_range = None

    update_parameters = ['frequency']

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.visa_server = yield self.cxn[self.visa_server_name]
        yield self.visa_server.select_interface(self.visa_address)

    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'SOUR{}:FREQ {}'.format(self.source, frequency)
        yield self.visa_server.write(command)

    @inlineCallbacks
    def get_frequency(self):
        command = 'SOUR{}:FREQ?'.format(self.source)
        ans = yield self.visa_server.query('FREQ:CW?')
        returnValue(float(ans))

