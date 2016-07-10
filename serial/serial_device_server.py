import json

from twisted.internet.defer import returnValue, inlineCallbacks
from labrad.server import LabradServer, setting

class SerialConnection():
    def __init__(self, serial_server, port, **kwargs):
        timeout = kwargs.get('timeout')
        baudrate = kwargs.get('baudrate')
        stopbits = kwargs.get('stopbits')
        bytesize = kwargs.get('bytesize')

        serial_server.open(port)

        if timeout is not None: 
            serial_server.timeout(timeout)
        if baudrate is not None: 
            serial_server.baudrate(baudrate)
        if stopbits is not None: 
            serial_server.stopbits(stopbits)
        if bytesize is not None: 
            serial_server.bytesize(bytesize)

        self.write = lambda s: serial_server.write(s)
        self.write_line = lambda s: serial_server.write_line(s)
        self.write_lines = lambda s: serial_server.write_lines(s)
        self.read = lambda x = 0: serial_server.read(x)
        self.read_line = lambda: serial_server.read_line()
        self.read_lines = lambda: serial_server.read_lines()
        self.close = lambda: serial_server.close()
        self.flushinput = lambda: serial_server.flushinput()
        self.flushoutput = lambda: serial_server.flushoutput()
        self.ID = serial_server.ID

class SerialDeviceServer(LabradServer):
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
            connection_name = device.serial_server_name + ' - ' + device.port
            if connection_name not in self.open_connections:
                params = dict(device.__dict__)
                params.pop('serial_server_name')
                params.pop('port')
                connection = yield self.init_serial(
                    device.serial_server_name,
                    device.port,
                    **params)
                self.open_connections[connection_name] = connection
            device.serial_connection = self.open_connections[connection_name]
            yield device.initialize()

    def init_serial(self, serial_server_name, port, **kwargs):
        serial_server = self.client.servers[serial_server_name]
        serial_server_connection = SerialConnection(
                serial_server=serial_server, port=port, **kwargs)
        print 'connection opened: {} - {}'.format(serial_server_name, port)
        return serial_server_connection

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
 
    def stopServer( self ):
        for connection in self.open_connections.values():
            connection.close()
