from twisted.internet.threads import deferToThread

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
        interface = yield deferToThread(self.connection.getsocketname()[0])
        response_message = yield self.send(op='start_link',
                                     params={ 'ip_address': interface })

    @inlineCallbacks
    def send(self, **kwargs):
        message = MSquaredMessage(**kwargs)
        message_json = message.to_json()
        yield deferToThread(self.connection.send(message_json))
        response_json = yield deferToThread(self.connection.recv(1024))
        return MSquaredMessage.from_json(response_json)
    
    @inlineCallbacks
    def set(self, setting, value, key_name='setting'):
        parameters = {key_name: value}
        if key_name == 'setting':
            parameters[key_name] = [parameters[key_name]]
        response_message = yield self.send(op=setting, parameters=parameters)
        ok = response_message.is_ok(status=[0])
        return bool(ok)
    
    @inlineCallbacks
    def get(self, setting):
        response_message = yield self.send(op=setting, parameters=None)
        if response_message.is_ok(status=[0]):
            return normalize_parameters(response_message.parameters)
        else:
            return None
