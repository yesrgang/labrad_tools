from devices.silver_pack17.silver_pack17 import SilverPack17

class NdFilter(SilverPack17):
    enabled = True
    serial_server_name = 'yesr20_serial'
    serial_address = 'COM11'

__device__ = NdFilter
