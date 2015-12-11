class DCVoltageConfig(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.query_string = 'meas? '
    
    def a2v(self, ans):
        return float(ans)

class Agilent349880AConfig(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
class ServerConfig(object):
    def __init__(self):
        self.name = '34980A'
        self.deviceName = 'Agilent Technologies 34980A'
        self.measurement_period = 60 # [s]
        
        srq_channels = {
            '1001': DCVoltageConfig(name='1001', is_active=True),
            '1002': DCVoltageConfig(name='1002', is_active=True),
            '1003': DCVoltageConfig(name='1003', is_active=True),
            '1004': DCVoltageConfig(name='1004', is_active=True),
            '1005': DCVoltageConfig(name='1005', is_active=True),
            '1006': DCVoltageConfig(name='1006', is_active=True),
            '1007': DCVoltageConfig(name='1007', is_active=True),
            '1008': DCVoltageConfig(name='1008', is_active=True),
            '1009': DCVoltageConfig(name='1009', is_active=True),
            }
       
        self.instruments = {
            'srq monitor': Agilent349880AConfig(
                gpib_device_id='yesr20 GPIB Bus - GPIB0::7', 
                channels=srq_channels,
                ),
            }
