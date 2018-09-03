from devices.ad9854.ad9854 import AD9854

class AOM(AD9854):
    autostart = True
    serial_server_name = "yesr10_serial"
    serial_address = "/dev/ttyACM649383339323514011E0"
    subaddress = 3

    default_frequency = 30e6

__device__ = AOM
