#import devices.ell7.ell7
#reload(devices.ell7.ell7)
from ell7.ell7 import ELL7

class H2RETRO(ELL7):
    autostart = False
    serial_server_name = 'yesr5_serial'
    serial_address = 'COM22'

__device__ = H2RETRO
