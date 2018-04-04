from devices.ad9854.ad9854 import AD9854

class AOM(AD9854):
    autostart = True
#    serial_server_name = "yesr20_serial"
#    serial_address = "COM6"
#    serial_server_name = "yesr10_serial"
    serial_server_name = "daisy_serial"
    serial_address = "/dev/ttyACM0"
    subaddress = 1

    default_frequency = 78.75e6

__device__ = AOM
