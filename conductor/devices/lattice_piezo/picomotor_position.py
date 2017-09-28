from labrad.wrappers import connectAsync
import sys
from twisted.internet.defer import inlineCallbacks

sys.path.append('../')
from conductor_device.conductor_parameter import ConductorParameter

class PicomotorPosition(ConductorParameter):
    priority = 2
    address = None
    axis = None
    previous_value = None

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync(name=self.name)
        yield self.cxn.yesr11_colorado_edu_socket.connect(self.address)
    
    @inlineCallbacks
    def update(self):
        if self.value != self.previous_value:
            yield self.cxn.yesr11_colorado_edu_socket.connect(self.address)
            command = '{}PA{}\n'.format(self.axis, self.value)
            yield self.cxn.yesr11_colorado_edu_socket.send(command)
            yield self.cxn.yesr11_colorado_edu_socket.close()
            self.previous_value = self.value
