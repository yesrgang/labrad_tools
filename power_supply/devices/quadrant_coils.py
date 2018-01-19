from devices.templates.psh6018 import PSH6018

class QuadrantCoils(PSH6018):
    autostart = True
    serial_server_name = 'yesr10_serial'
    serial_address = '/dev/ttyUSB0'

