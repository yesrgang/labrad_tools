import aosense_ecdl.aosense_ecdl
reload(aosense_ecdl.aosense_ecdl)
from aosense_ecdl.aosense_ecdl import AOSenseECDL

class BlueMaster(AOSenseECDL):
    autostart = False
    serial_server_name = 'yesr20_serial'
    serial_address = 'COM12'

    default_diode_current = 173.0 # [mA]

__device__ = BlueMaster
