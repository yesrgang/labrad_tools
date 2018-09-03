import devices.ad9956.ad9956
reload(devices.ad9956.ad9956)
from devices.ad9956.ad9956 import AD9956

class Channel(AD9956):
    autostart = True
    serial_server_name = "yesr10_serial"
#    serial_address = "/dev/ttyACM649383339323514011E0"
    serial_address = "/dev/ttyACMdumb"
    board_num = 0
    channel = 0

    default_frequency = 0e6

__device__ = Channel
