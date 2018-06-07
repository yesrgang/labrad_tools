import devices.verdi.verdi
reload(devices.verdi.verdi)
from devices.verdi.verdi import Verdi

class M2Verdi(Verdi):
    autostart = False
    serial_server_name = 'yesr20_serial'
    serial_address = 'COM19'

    power_range = (0.0, 18.0) # [W]

    default_power = 18.0 # [W]

__device__ = M2Verdi
