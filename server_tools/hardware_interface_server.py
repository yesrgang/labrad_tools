from labrad.server import LabradServer, setting

class InterfaceNotSelected(Exception):
    """ context has no selected interface for this server instance 
    
    If you have previously selected an interface, this server may have been 
    restarted and you must call "select_interface" again.
    """

class HardwareInterfaceServer(LabradServer):
    """ Template for hardware interface server """

    def initServer(self):
        self.interfaces = {}
        self.refresh_available_interfaces()

    def stopServer(self):
        """ notify connected device servers of closing connetion"""

    def refresh_available_interfaces(self):
        """ fill self.interfaces with available hardware """

    def call_if_available(self, f, c, *args, **kwargs):
        try:
            interface = self.get_interface(c)
            ans = getattr(interface, f)(*args, **kwargs)
            return ans
        except:
            self.refresh_available_interfaces()
            interface = self.get_interface(c)
            return getattr(interface, f)(*args, **kwargs)

    def get_interface(self, c):
        if 'address' not in c:
            raise InterfaceNotSelected
        if c['address'] not in self.interfaces.keys():
            self.refresh_available_interfaces()
            if c['address'] not in self.interfaces.keys():
                message = c['address'] + 'is unavailable'
                raise Exception(message)
        return self.interfaces[c['address']]

    @setting(0, returns='*s')
    def list_interfaces(self, c):
        """Get a list of available interfaces"""
        self.refresh_available_interfaces()
        return sorted(self.interfaces.keys())

    @setting(1, address='s', returns='s')
    def select_interface(self, c, address):
        self.refresh_available_interfaces()
        if address not in self.interfaces:
            message = c['address'] + 'is unavailable'
            raise Exception(message)
        c['address'] = address
        return c['address'] 
