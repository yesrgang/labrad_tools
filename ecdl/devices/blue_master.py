from aosense_ecdl.aosense_ecdl import AosenseEcdl

class BlueMaster(AosenseEcdl):
    autostart = False
    serial_server_name = 'yesr20_serial'
    serial_address = 'COM12'

    default_diode_current = 140.0 # [mA]

__device__ = BlueMaster
