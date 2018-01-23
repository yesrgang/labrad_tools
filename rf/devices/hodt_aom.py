from devices.ad9854.ad9854 import AD9854

class HODTAOM(AD9854):
    serial_server_name = "yesr20_serial"
    serial_address = "COM6"
    subaddress = 3

    default_frequency = 30e6

__device__ = HODTAOM
