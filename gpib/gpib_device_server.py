import json

from twisted.internet.defer import returnValue, inlineCallbacks
from labrad.server import LabradServer, setting

class GPIBConnection():
    def __init__(self, gpib_server, address, timeout=None):
        self.context = gpib_server.context()
        self.gpib_server = gpib_server

        gpib_server.address(address, context=self.context)
        gpib_server.timeout(timeout, context=self.context)


    def write(self, data):
        return self.gpib_server.write(data, context=self.context)

    def read(self, n_bytes=None):
        return self.gpib_server.read(n_bytes, context=self.context)

    def query(self, data):
        return self.gpib_server.query(data, context=self.context)

    def list_devices(self):
        return self.gpib_server.list_devices(context=self.context)

class GPIBDeviceServer(LabradServer):
    def __init__(self, config_path='config'):
        LabradServer.__init__(self)
        self.devices = {}
        self.open_connections = {}

        self.load_config(config_path)

    def load_config(self, path=None):
        if path is not None:
            self.config_path = path
        config = __import__(self.config_path).ServerConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def initServer(self):
        for device in self.devices.values():
            connection_name = device.gpib_server_name + ' - ' + device.address
            if connection_name not in self.open_connections:
                connection = yield self.init_gpib_connection(
                    device.gpib_server_name,
                    device.address,
                    device.timeout)
                self.open_connections[connection_name] = connection
            device.gpib_connection = self.open_connections[connection_name]
            yield device.initialize()


    def init_gpib_connection(self, gpib_server_name, address, timeout):
        gpib_server = self.client.servers[gpib_server_name]
        gpib_server_connection = GPIBConnection(gpib_server, address, timeout)
        print 'connection opened: {} - {}'.format(gpib_server_name, address)
        return gpib_server_connection

    @setting(0, returns='s')
    def get_device_list(self, c):
        return json.dumps(self.devices.keys())
    
    @setting(1, name='s', returns='s')
    def select_device_by_name(self, c, name):
        if name not in self.devices.keys():
            message = '{} is not the name of a configured device'.format(name)
            raise Exception(message)
        
        c['name'] = name
        device = self.get_device(c)
        return json.dumps(device.__dict__, default=lambda x: None)

    def get_device(self, c):
        name = c.get('name')
        if name is None:
            raise Exception('select a device first')
        return self.devices[name]
