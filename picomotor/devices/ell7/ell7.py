#import socket

from server_tools.device_server import Device
from twisted.internet.defer import inlineCallbacks, returnValue
import time

class ELL7(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.5
    serial_baudrate = 9600

    # 2048 imp/mm
#    impPERmm = 2048.

    update_parameters = ['position']


    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)
        self.serial_server.timeout(self.serial_timeout)
        yield self.serial_server.baudrate(self.serial_baudrate)
        #baclk to home position
        yield self.serial_server.write_line('0ho0')
        time.sleep(0.1)
        resp = yield self.serial_server.read_lines()
        #2048 imp/mm for ELL7
#        if resp[0][1:3] == 'PO':
#            print 'Home position = {:.3f} (mm)'.format(int(resp[0][3:])/impPERmm, 16)
#        else:
#            print 'Do NOT come back to home position!'

    @inlineCallbacks
    def set_position(self, position):
        impPERmm = 2048
        yield self.serial_server.read_lines()
        time.sleep(0.1)
        # range of ELL7, 25mm
        pos = int(position) if position < 25 else 24
        if pos == 0:
            pos_hex = '0000'
        elif pos == 1:
            pos_hex = '0800'
        else:
            pos_hex = hex(pos*impPERmm)

        n = len(pos_hex)
        pos_hex = pos_hex[n-4:n].upper()

        command = '0ma0000' + pos_hex
        yield self.serial_server.write_line(command)
 #       time.sleep(0.5)
        yield self.serial_server.read_lines()
#        n = len(resp[0])
#        cpos = float(int(resp[0][n-4:n], 16))/impPERmm
 #       print  'current position = {:.2f} (mm)'.format(cpos)

    @inlineCallbacks
    def get_position(self):
        impPERmm = 2048
        yield self.serial_server.read_lines()
        time.sleep(0.1)
        yield self.serial_server.write_line('0gp')
#        time.sleep(0.5)
        resp = yield self.serial_server.read_lines()
        n = len(resp[0])
        cpos = float(int(resp[0][n-4:n], 16))/impPERmm
#        print  'current position = {:.2f} (mm)'.format(cpos)      
        returnValue(int(round(cpos)))
