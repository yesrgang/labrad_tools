class SerialConnection():
    def __init__(self, server, device):
        server.open(device.address)
        
        for attr in ['timeout', 'baudrate', 'stopbits', 'bytesize']:
            if hasattr(device, attr): 
                value = getattr(device, attr)
                getattr(server, attr)(value)

        self.write = lambda s: server.write(s)
        self.write_line = lambda s: server.write_line(s)
        self.write_lines = lambda s: server.write_lines(s)
        self.read = lambda x = 0: server.read(x)
        self.read_line = lambda: server.read_line()
        self.read_lines = lambda: server.read_lines()
        self.close = lambda: server.close()
        self.flushinput = lambda: server.flushinput()
        self.flushoutput = lambda: server.flushoutput()
        self.ID = server.ID
