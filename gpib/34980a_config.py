class DCVoltageConfig(object):
    def __init__(self):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.query_string = 'meas? '

srq_channels = {
                '1001': DCVoltageConfig()
                }



class Agilent349880AConfig(object):
    def __init__(self):
        for key, value in kwargs.items():
            setattr(self, key, value)
        


class ServerConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE 34980A'
        self.deviceName = 'Agilent Technologies 34980A'
        self.instruments = {'srq monitor': Agilent349880AConfig(gpib_device_id='yesr10 GPIB Bus - GPIB0::9', 
                                                                channels=srq_channels),
                           }


