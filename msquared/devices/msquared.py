import json

from twisted.internet.threads import deferToThread
from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceWrapper
from lib.msquared_message import MSquaredMessage
from lib.helpers import normalize_parameters

class MSquared(DeviceWrapper):
    """" template for configuration """
    def __init__(self, config):
        self.update_parameters = []
        self.init_commands = []
        for key, value in config.items():
            setattr(self, key, value)
        super(MSquared, self).__init__({})
    
    @inlineCallbacks
    def initialize(self):
        interface = yield self.connection.getsockname()
        response_message = yield self.send(op='start_link',
                                     parameters={ 'ip_address': interface[0]})

    @inlineCallbacks
    def send(self, **kwargs):
        message = MSquaredMessage(**kwargs)
        message_json = message.to_json()
        yield self.connection.send(message_json)
        response_json = yield self.connection.recv(1024)
        returnValue(MSquaredMessage.from_json(response_json))
    
    @inlineCallbacks
    def set(self, setting, value, key_name='setting'):
        parameters = {key_name: value}
        if key_name == 'setting':
            parameters[key_name] = [parameters[key_name]]
        response_message = yield self.send(op=setting, parameters=parameters)
        ok = response_message.is_ok(status=[0])
        returnValue(bool(ok))
    
    @inlineCallbacks
    def get(self, setting):
        response_message = yield self.send(op=setting, parameters=None)
        if response_message.is_ok(status=[0]):
            returnValue(normalize_parameters(response_message.parameters))
        else:
            returnValue(None)
