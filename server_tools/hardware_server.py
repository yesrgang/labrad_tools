from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks

class HardwareCommunicationServer(LabradServer):
    """ Template for hardware communication server """

    def initServer(self):
        self.refresh_available_hardware()

    def stopServer(self):
        """ notify connected device servers of closing connetion"""

    def refresh_available_hardware(self):
        """ fill self.hardware with available connections """
        self.hardware = {}

    def get_connection(self, c):
        if 'address' not in c:
            raise Exception('no hardware selected')
        if c['address'] not in self.hardware:
            self.refresh_available_hardware()
            if c['address'] not in self.hardware:
                raise Exception(c['address'] + 'is unavailable')
        return self.hardware[c['address']]

    @setting(0, returns='*s')
    def get_hardware_list(self, c):
        """Get a list of available hardware"""
        self.refresh_available_hardware()
        return sorted(self.hardware.keys())

    @setting(1, address='s', returns='s')
    def connect(self, c, address):
        self.refresh_available_hardware()
        if address not in self.hardware:
            raise Exception(c['address'] + 'is unavailable')
        c['address'] = address
        return c['address'] 
