from devices.sprout.sprout import Sprout

class M2Sprout(Sprout):
    autostart = False
    serial_server_name = 'yesr5_serial'
    serial_address = 'COM9'

__device__ = M2Sprout
