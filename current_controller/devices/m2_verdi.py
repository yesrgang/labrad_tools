from devices.verdi.verdi import Verdi

class M2Verdi(Verdi):
    autostart = False
    serial_server_name = 'yesr20_serial'
    serial_address = 'COM19'

    power_range = (0.0, 18.0) # [W]
    default_power = 18.0 # [W]
    warmup_power = 14.0 # [W]
    shutter_delay = 600 # [s]
    full_power_delay = 1800 # [s]

__device__ = M2Verdi
