class LDC80xxConfig(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class PRO8000Config(object):
    def __init__(self):
        self.servername = 'yesr20_pro8000'
        self.updatetime = 100 # [ms]
        self.state_id = 461001
        self.current_id = 461002
        self.power_id = 461003
