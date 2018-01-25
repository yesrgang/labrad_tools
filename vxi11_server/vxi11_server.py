"""
### BEGIN NODE INFO
[info]
name = vxi11
version = 1
description = none
instancename = %LABRADNODE%_vxi11

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import sys
import vxi11

from labrad.server import LabradServer, setting

sys.path.append('../')
from server_tools.hardware_interface_server import HardwareInterfaceServer


class VXI11Server(HardwareInterfaceServer):
    """ Provides access to vxi specified ethernet connected hardware.
    
    this server can be used to access vxi11 enabled devices on the in-lab network 
    when the client is itself not on the in-lab network.
    """
    name = '%LABRADNODE%_vxi11'

    def refresh_available_interfaces(self):
        """ fill self.interfaces with available connections """
	addresses = vxi11.list_devices('192.168.1.255')
        for address in addresses:
            self.interfaces[address] = vxi11.Instrument(address)

    @setting(3, data='s', returns='')
    def write(self, c, data):
        """Write a string to the vxi interface."""
        self.call_if_available('write', c, data)

    @setting(4, n_bytes='w', returns='s')
    def read(self, c, n_bytes=None):
        """Read from the vxi interface."""
        response = self.call_if_available('read', c)
        return response.strip()

    @setting(5, data='s', returns='s')
    def ask(self, c, data):
        """Make a query, writes string then returns instrument response."""
        response = self.call_if_available('ask', c, data)
        return response.strip()

    @setting(6, timeout='v', returns='v')
    def timeout(self, c, timeout=None):
	"""set interface timeout"""
        interface = self.get_interface(c)
        if timeout is not None:
            interface.timeout = timeout
        return interface.timeout

if __name__ == '__main__':
    from labrad import util
    util.runServer(VXI11Server())
