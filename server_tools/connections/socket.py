import socket

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

class SocketConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield deferToThread(
                socket.create_connection((device.servername, device.address), 
                                         timeout=5))

    @inlineCallbacks 
    def send(self, value):
        response = yield deferToThread(self.connection.send, value)
        returnValue(response)
    
    @inlineCallbacks 
    def recv(self, value):
        response = yield deferToThread(self.connection.recv, value)
        returnValue(response)
