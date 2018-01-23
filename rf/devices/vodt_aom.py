from devices.ad9854.ad9854 import AD9854

class VODTAOM(AD9854):
    serial_server_name = "yesr20_serial"
    serial_address = "COM6"
    subaddress = 4

    default_frequency = 30.2e6

__device__ = VODTAOM
