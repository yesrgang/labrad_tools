from devices.ad9854.ad9854 import AD9854

class DimpleAOM(AD9854):
    serial_server_name = "yesr20_serial"
    serial_address = "COM6"
    subaddress = 5

    default_frequency = 80.0e6

__device__ = DimpleAOM
