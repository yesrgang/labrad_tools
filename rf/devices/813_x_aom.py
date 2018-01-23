from devices.ad9854.ad9854 import AD9854

class AOM813X(AD9854):
    serial_server_name = "yesr20_serial"
    serial_address = "COM6"
    subaddress = 0

    default_frequency = 81.25e6

__device__ = AOM813X
