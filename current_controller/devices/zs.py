from devices.ldc80xx.ldc80xx import Ldc80xx

class BlueZS(Ldc80xx):
    autostart = False
    gpib_server_name = 'yesr20_gpib'
    gpib_address = 'GPIB0::9::INSTR'

    pro8_slot = 6
    default_current = 0.1500

__device__ = BlueZS
