import socket

from server_tools.device_server import Device
from twisted.internet.defer import inlineCallbacks, returnValue


class NF8742(Device):
    socket_address = None
    socket_timeout = 0.5
    socket_buffer_size = 1024

    controller_axis = None
    update_parameters = ['position']

    def initialize(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.socket_timeout)
        self.socket.connect(self.socket_address)
        try:
            self.socket.recv(self.socket_buffer_size)
        except socket.timeout:
            pass

    def terminate(self):
        self.socket.close()

    def set_position(self, position):
        command = '{}PA{}\n'.format(self.controller_axis, position)
        self.socket.send(command)

    def get_position(self):
        command = '{}PA?\n'.format(self.controller_axis)
        self.socket.send(command)
        response = self.socket.recv(self.socket_buffer_size)
        returnValue(int(response.strip().replace(' ', '')))
