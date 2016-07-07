import json
import os.path

from vxi11 import Instrument
from labrad.server import LabradServer, setting

class AG335XXXServer(LabradServer):
    """
    Agilent arbitrary waveform generator
    """
    name = 'ag335xxx'

    def __init__(self, config_path='config'):
        self.load_config(config_path)
        LabradServer.__init__(self)

    def load_config(self, path=None):
        if path is not None:
            self.config_path = path

        config = __import__(self.config_path).ServerConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    def stopServer(self):
        for device in self.devices.values():
            if device.connection:
                devivce.connection.close()

    def get_connection(self, c):
        name = c.get('name')
        if name is None:
            raise Exception('select a device first.')
        return self.devices[name].connection

    @setting(0, name='s', returns='s')
    def select_device_by_name(self, c, name):
        c['name'] = name
        if name in self.devices.keys():
            device = self.devices[name]
            if not device.connection:
                host = device.host
                device.connection = Instrument(host)
            for command in device.init_commands:
                yield device.connection.write(command)
            returnValue(name)
        else:
            returnValue(json.dumps(self.devices.keys()))

    @setting(1, returns='b')
    def reset(self, c):
        connection = self.get_conenction(c)
        yield connection.write('*RST')
        returnValue(True)

    @setting(2, waveform='s', returns='b')
    def program_waveform(self, c, waveform):
        connection = self.get_connection(c)
        channel = self.devices[c['name']].channel
        waveform = json.loads(waveform)
        
        commands = [
            'SOUR{}:DATA:VOL:CLE'.format(channel),
            ('SOUR{}:DATA:ARB '.format(channel), waveform['name'], ', ', str(waveform['points'])),
            ('SOUR{}:FUNC:ARB '.format(channel), waveform['name']),
            ('SOUR{}:FUNC:ARB:SRAT '.format(channel), str(waveform['sample rate'])),
        ]

        for command in commands:
            connection.write(command)

        returnValue(True)

if __name__ == '__main__':
    from labrad import util

    server = AG335XXXServer()
    util.runServer(server)
