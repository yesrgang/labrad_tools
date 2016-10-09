"""
### BEGIN NODE INFO
[info]
name = gpib
version = 1
description =
instancename = %LABRADNODE%_gpib

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import visa

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callLater

from server_tools.hardware_communication_server import HardwareCommunicationServer


class GPIBServer(HardwareCommunicationServer):
    """Provides direct access to GPIB-enabled hardware."""
    name = '%LABRADNODE%_gpib'

    def refresh_available_hardware(self):
        """ fill self.hardware with available connections """
        rm = visa.ResourceManager()
        addresses = rm.list_resources()
        additions = set(addresses) - set(self.devices.keys())
        deletions = set(self.devices.keys()) - set(addresses)
        for address in additions:
            if address.startswith('GPIB'):
                inst = rm.get_instrument(address)
                inst.write_termination = ''
                inst.clear()
                self.hardware[address] = inst
                print 'connected to GPIB device ' + address
        for addr in deletions:
            del self.devices[addr]
            self.sendDeviceMessage('GPIB Device Disconnect', addr)

    @setting(3, data='s', returns='')
    def write(self, c, data):
        """Write a string to the GPIB bus."""
        connection = self.get_connection(c)
        connection.write(data)

    @setting(4, n_bytes='w', returns='s')
    def read(self, c, n_bytes=None):
        """Read from the GPIB bus.

        If specified, reads only the given number of bytes.
        Otherwise, reads until the device stops sending.
        """
        connection = self.get_connection(c)
        ans = connection.read_raw()
        return str(ans).strip()

    @setting(5, data='s', returns='s')
    def query(self, c, data):
        """Make a GPIB query, a write followed by a read.

        This query is atomic.  No other communication to the
        device will occur while the query is in progress.
        """
        connection = self.get_connection(c)
        connection.write(data)
        ans = connection.read_raw()
        return str(ans).strip()

if __name__ == '__main__':
    from labrad import util
    util.runServer(GPIBServer())
