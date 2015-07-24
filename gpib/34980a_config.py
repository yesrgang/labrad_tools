class DCVoltageConfig(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.query_string = 'meas? '
	
    def ans_to_value(self, ans):
        return float(ans)

srq_channels = {
                '1001': DCVoltageConfig(name='1001', is_active=True),
                '1002': DCVoltageConfig(name='1002', is_active=True),
                }



class Agilent349880AConfig(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        


class ServerConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% 34980A'
        self.deviceName = 'Agilent Technologies 34980A'
        self.instruments = {'srq monitor': Agilent349880AConfig(gpib_device_id='yesr20 GPIB Bus - GPIB0::9', 
                                                                channels=srq_channels),
                           }


