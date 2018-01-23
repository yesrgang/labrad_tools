from devices.psh6018.psh6018 import PSH6018

class QuadrantCoils(PSH6018):
    autostart = True
    serial_server_name = 'yesr10_serial'
    serial_address = '/dev/ttyUSB0'

__device__ = QuadrantCoils
