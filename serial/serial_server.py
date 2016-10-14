"""
### BEGIN NODE INFO
[info]
name = serial
version = 1.1
description = 
instancename = %LABRADNODE%_serial

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import sys

from time import sleep

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from serial import Serial
import serial.tools.list_ports

sys.path.append('../')
from server_tools.hardware_interface_server import HardwareInterfaceServer

class SerialServer(HardwareInterfaceServer):
    """Provides access to hardware's serial interface """
    name = '%LABRADNODE%_serial'

    def refresh_available_interfaces(self):
        if sys.platform.startswith('win32'):
            try_ports = ['COM{}'.format(i) for i in range(1, 20)]
        else:
            try_ports = [cp[0] for cp in serial.tools.list_ports.comports()]
        
        addresses = []
        for address in try_ports:
           try:
               ser = Serial(address)
               ser.close()
               addresses.append(address)
               if address not in self.interfaces.keys():
                   print '{} available'.format(address)
           except:
               pass
        
        additions = set(addresses) - set(self.interfaces.keys())
        deletions = set(self.interfaces.keys()) - set(addresses)
        for address in additions:
            ser = Serial(address)
            ser.setTimeout(0)
            ser.close()
            self.interfaces[address] = ser
        for addr in deletions:
            del self.interfaces[addr]
    
    def get_connection(self, c):
        interface = super(SerialServer, self).get_connection(c)
        if not interface.isOpen():
            interface.open()
        return interface
    
    @setting(2, returns='b')
    def disconnect(self, c):
        self.refresh_available_interfaces()
        if c['address'] not in self.interfaces:
            raise Exception(c['address'] + 'is unavailable')
        interface = self.get_connection(c)
        interface.close()
        del c['address']
        return True

    @setting(3, baudrate='w', returns='w')
    def baudrate(self, c, baudrate=None):
        if baudrate is not None:
            self.call_if_available('setBaudrate', c, baudrate)
        baudrate = self.call_if_available('getBaudrate', c)
        return baudrate

    @setting(4, bytesize='w', returns='w')
    def bytesize(self, c, bytesize=None):
        if bytesize is not None:
            self.call_if_available('setByteSize', c, bytesize)
        bytesize = self.call_if_available('getByteSize', c)
        return bytesize
    
    @setting(5, parity='s', returns='s')
    def parity(self, c, parity=None):
        if parity is not None:
            self.call_if_available('setParity', c, parity)
        parity = self.call_if_available('getParity', c)
        return parity

    @setting(6, stopbits='w', returns='w')
    def stopbits(self, c, stopbits=None):
        if stopbits is not None:
            self.call_if_available('setStopBits', c, stopbits)
        stopbits = self.call_if_available('getStopBits', c)
        return stopbits

    @setting(7, timeout='w', returns='w')
    def timeout(self, c, timeout=None):
        if timeout is not None:
            self.call_if_available('setTimeout', c, timeout)
        timeout = self.call_if_available('getTimeout', c)
        return timeout

    @setting(8, rts='b', returns='s')
    def rts(self, c, rts=None):
        self.call_if_available('setRTS', c, rts)

    @setting(9, dtr='b', returns='s')
    def dtr(self, c, dtr=None):
        self.call_if_available('setDTR', c, dtr)

    @setting(10, data=['s: string', '*w: bytes'], returns='w: num bytes sent')
    def write(self, c, data):
        """Sends data over the port."""
        self.call_if_available('write', c, data)
        return long(len(data))

    @setting(11, data=['s: string', '*w: bytes'], returns='w: num bytes sent')
    def write_line(self, c, data):
        """Sends data over the port. appends CR LF."""
        data += '\r\n'
        self.call_if_available('write', c, data)
        return long(len(data))

    @setting(12, n_bytes='w', returns='s')
    def read(self, c, n_bytes=None):
        ans = self.call_if_available('read', c, n_bytes)
        return ans
    
    @setting(13, returns='s')
    def read_line(self, c):
        ans = self.call_if_available('readline', c)
        return ans.strip()

    @setting(14, n_lines='w', returns='*s')
    def read_lines(self, c, n_lines):
        ans = self.call_if_available('readlines', c, n_lines)
        return [a.strip() for a in ans]

__server__ = SerialServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
