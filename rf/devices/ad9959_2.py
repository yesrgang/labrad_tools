import devices.ad9959.ad9959
reload(devices.ad9959.ad9959)
from devices.ad9959.ad9959 import AD9959

class Channel(AD9959):
    autostart = True
    serial_server_name = "yesr10_serial"
    serial_address = "/dev/ttyACM1"
#    serial_server_name = "yesr20_serial"
#    serial_address = "COM21"
    board_num = 0
    channel = 2

    default_frequency = 0e6

__device__ = Channel
