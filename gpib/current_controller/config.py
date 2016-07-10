from devices.ldc80xx import LDC80xx

class ServerConfig(object):
    def __init__(self):
        self.devices = {
            '3d': LDC80xx(
                gpib_server_name='yesr20_gpib_bus',
                address='GPIB0::9::INSTR',
                slot=2,
                current_range=[0, .153],
                default_current=.1498,
                current_stepsize=1e-4,
            ),
            '2d': LDC80xx(
                gpib_server_name='yesr20_gpib_bus',
                address='GPIB0::9::INSTR',
                slot=4,
                current_range=[0, .153],
                default_current=.1511,
                current_stepsize=1e-4,
            ),
            'zs': LDC80xx(
                gpib_server_name='yesr20_gpib_bus',
                address='GPIB0::9::INSTR',
                slot=6,
                current_range=[0, .153],
                default_current=.1486,
                current_stepsize=1e-4,
            ),
        }
