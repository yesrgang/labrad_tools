import devices.ad9959.ad9959
reload(devices.ad9959.ad9959)
from devices.ad9959.ad9959 import AD9959

class Channel(AD9959):
    autostart = True
    serial_server_name = "yesr10_serial"
    serial_address = "/dev/ttyACM853323434323510101E0"
    board_num = 0
    channel = 0

    default_frequency = 0e6

__device__ = Channel
