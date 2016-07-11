import labrad.units as U

class GPIBConnection():
    def __init__(self, server, device):
        self.context = server.context()
        self.server = server

        server.address(device.address, context=self.context)
        if hasattr(device, 'timeout'):
            server.timeout(device.timeout, context=self.context)
        else:
            server.timeout(1 * U.s, context=self.context)

    def write(self, data):
        return self.server.write(data, context=self.context)

    def read(self, n_bytes=None):
        return self.server.read(n_bytes, context=self.context)

    def query(self, data):
        return self.server.query(data, context=self.context)

    def list_devices(self):
        return self.server.list_devices(context=self.context)
