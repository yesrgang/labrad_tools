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
        addresses = []
        if sys.platform.startswith('win32'):
            for i in range(1, 20):
                address = 'COM{}'.format(i)
                try:
                    ser = Serial(address)
                    ser.close()
                    addresses.append(address)
                except:
                    pass
        else:
            dev_list = serial.tools.list_ports.comports()
            for cp in serial.tools.list_ports.comports():
                address = cp[0]
                try:
                    ser = Serial(address)
                    ser.close()
                    addresses.append(address)
                except:
                    pass

        additions = set(addresses) - set(self.interfaces.keys())
        deletions = set(self.interfaces.keys()) - set(addresses)
        for address in additions:
            ser = Serial(address)
            ser.close()
            self.interfaces[address] = ser
        for addr in deletions:
            del self.interfaces[addr]

    @setting(3, baudrate='w', returns='w')
    def baudrate(self, c, baudrate=None):
        self.call_if_available('open', c)
        if baudrate is not None:
            self.call_if_available('setBaudrate', c, baudrate)
        baudrate = self.call_if_available('getBaudrate', c)
        self.call_if_available('close', c)
        return baudrate

    @setting(4, bytesize='w', returns='w')
    def bytesize(self, c, bytesize=None):
        self.call_if_available('open', c)
        if bytesize is not None:
            self.call_if_available('setByteSize', c, bytesize)
        bytesize = self.call_if_available('getByteSize', c)
        self.call_if_available('close', c)
        return bytesize
    
    @setting(5, parity='s', returns='s')
    def parity(self, c, parity=None):
        self.call_if_available('open', c)
        if parity is not None:
            self.call_if_available('setParity', c, parity)
        parity = self.call_if_available('getParity', c)
        self.call_if_available('close', c)
        return parity

    @setting(6, stopbits='s', returns='s')
    def stopbits(self, c, stopbits=None):
        self.call_if_available('open', c)
        if stopbits is not None:
            self.call_if_available('setStopBits', c, stopbits)
        stopbits = self.call_if_available('getStopBits', c)
        self.call_if_available('close', c)
        return stopbits

    @setting(7, timeout='s', returns='s')
    def timeout(self, c, timeout=None):
        self.call_if_available('open', c)
        if timeout is not None:
            self.call_if_available('setTimeout', c, timeout)
        timeout = self.call_if_available('getTimeout', c)
        self.call_if_available('close', c)
        return timeout

    @setting(8, rts='s', returns='s')
    def rts(self, c, rts=None):
        self.call_if_available('open', c)
        self.call_if_available('setRTS', c, rts)
        self.call_if_available('close', c)

    @setting(9, dtr='s', returns='s')
    def dtr(self, c, dtr=None):
        self.call_if_available('open', c)
        self.call_if_available('setDTR', c, dtr)
        self.call_if_available('close', c)


    @setting(10, data=['s: string', '*w: bytes'], returns='w: num bytes sent')
    def write(self, c, data):
        """Sends data over the port."""
        self.call_if_available('open', c)
        if not isinstance(data, str):
            data = ''.join(chr(x & 255) for x in data)
        self.call_if_available('write', c, data)
        self.call_if_available('close', c)
        return long(len(data))

    @setting(11, data=['s: string', '*w: bytes'], returns='w: num bytes sent')
    def write(self, c, data):
        """Sends data over the port. appends CR LF."""
        self.call_if_available('open', c)
        if not isinstance(data, str):
            data = ''.join(chr(x & 255) for x in data)
        data += '\r\n'
        self.call_if_available('write', c, data)
        self.call_if_available('close', c)
        return long(len(data))

    @setting(12, n_bytes='w', returns='s')
    def read(self, c, n_bytes=None):
        self.call_if_available('open', c)
        ans = self.call_if_available('read', c, n_bytes)
        self.call_if_available('close', c)
        return ans
    
    @setting(13, returns='s')
    def readline(self, c):
        self.call_if_available('open', c)
        ans = self.call_if_available('readline', c)
        self.call_if_available('close', c)
        return ans

    @setting(14, n_lines='w', returns='s')
    def readlines(self, c, n_lines):
        self.call_if_available('open', c)
        ans = self.call_if_available('readlines', c, n_lines)
        self.call_if_available('close', c)
        return ans

__server__ = SerialServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
