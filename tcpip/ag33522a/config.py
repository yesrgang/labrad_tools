class DeviceConfig(object):
    def __init__(self, host=None, channel=None, default_settings=None, **kwargs):
        self.connection = None
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.devices = {
            'alpha fm': DeviceConfig(
                host=('sr3waveform.colorado.edu', 5025),
                channel=1,
                default_settings=[
                    'OUTP1:LOAD 50',
                    'SOUR1:VOLT 2',
                    'SOUR1:VOLT:OFFS 0',
                    'SOUR1:BURS:NCYC 1',
                    'TRIG1:SOUR EXT',
                    'OUTP1 1',
                ]
            ),
            'beta fm': DeviceConfig(
                host=('sr3waveform.colorado.edu', 5025),
                channel=2,
                default_settings=[
                    'OUTP2:LOAD 50',
                    'SOUR2:VOLT 2',
                    'SOUR2:VOLT:OFFS 0',
                    'SOUR2:BURS:NCYC 1',
                    'TRIG2:SOUR EXT',
                    'OUTP2 1',
                ]
            ),
        }
