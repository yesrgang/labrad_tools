from devices.ldc80xx.ldc80xx import Ldc80xx

class Blue3D(Ldc80xx):
    autostart = False
    gpib_server_name = 'yesr20_gpib'
    gpib_address = 'GPIB0::9::INSTR'

    pro8_slot = 2
    default_current = 0.1498

__device__ = Blue3D
