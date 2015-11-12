import json
import socket

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks

class AG33522AServer(LabradServer):
    def __init__(self, config_filename):
        self.config_filename = config_filename
        self.load_configuration()
        LabradServer.__init__(self)
    
    def load_configuration(self):
        config = __import__(self.config_filename).ServerConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)
    
    def initServer(self):
        self.write_defaults()
    
    def write_defaults(self):
        for name, channel in self.channels.items():
            self.send_to_device(name, *channel.default_settings)

    def send_to_device(self, name, *commands):
        channel = self.channels[name]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(channel.address)
        for c in commands:
            s.send(''.join(c) + '\r\n')
        s.close()
    
    @setting(1, 'program_waveform', waveform='s')
    def program_waveform(self, c, waveform):
        waveform = json.loads(waveform)
        channel = self.channels[waveform['channel name']]
        commands = [
            'SOUR{}:DATA:VOL:CLE'.format(channel.output),
            ('SOUR{}:DATA:ARB '.format(channel.output), waveform['name'], ', ', str(waveform['points'])[1:-1]),
            ('SOUR{}:FUNC:ARB '.format(channel.output), waveform['name']),
            ('SOUR{}:FUNC:ARB:SRAT '.format(channel.output), str(waveform['sample rate'])),
            ]
        self.send_to_device(waveform['channel name'], *commands)



if __name__ == '__main__':
    from labrad import util
    config_filename = 'ag33522a-config'
    server = AG33522AServer(config_filename)
    util.runServer(server)
