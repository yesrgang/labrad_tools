from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

class Connection(object):
    @inlineCallbacks
    def connect(self, device):
        connection_name = '{} - {}'.format(device.server_name, device.name)
        self.connection = yield connectAsync(name=connection_name)
