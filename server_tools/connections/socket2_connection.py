import socket

from twisted.internet.defer import inlineCallbacks, returnValue

class Socket2Connection(object):
    @inlineCallbacks
    def initialize(self, device):
        yield None

        self.address = (device.servername, int(device.address))
        self.timeout = device.timeout
        try:
            self.connect()
            self.connection.recv(1024)
            self.connection.close()
        except socket.timeout:
            self.connection.close()

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(self.timeout)
        self.connection.connect(self.address)
        try:
            self.connection.recv(1024)
        except socket.timeout:
            pass

    @inlineCallbacks 
    def send(self, value):
        yield None
        self.connect()
        response = self.connection.send(value)
        self.connection.close()
        returnValue(response)
    
    @inlineCallbacks 
    def recv(self, value=1024):
        yield None
        self.connect()
        response = self.connection.recv(value)
        self.connection.close()
        returnValue(response)
    
    @inlineCallbacks 
    def query(self, value, buffer_size=1024):
        yield None
        self.connect()
        self.connection.send(value)
        response = self.connection.recv(buffer_size)
        self.connection.close()
        returnValue(response)
    
    @inlineCallbacks
    def getsockname(self):
        yield None
        returnValue(self.connection.getsockname())
