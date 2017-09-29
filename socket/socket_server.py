"""
### BEGIN NODE INFO
[info]
name = socket
version = 1.0
description = 
instancename = %LABRADNODE%_socket

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer
from labrad.server import setting
from labrad.server import Signal

import socket

class SocketServer(LabradServer):
    name = '%LABRADNODE%_socket'

    @setting(10, 'connect', address='si', returns='b')
    def connect(self, c, address):
        c['address'] = address
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(address)
        c['socket'] = s
        return True

    @setting(11, 'send', command='s', returns='b')
    def send(self, c, command):
        s = c['socket']
        s.send(command)
        return True
    
    @setting(12, 'recv', nbytes='i', returns='s')
    def recv(self, c, nbytes=4096):
        s = c['socket']
        ans = s.recv(nbytes)
        return ans
    
    @setting(13, 'close', returns='b')
    def close(self, c):
        s = c['socket']
        s.close()
        return True


if __name__ == "__main__":
    from labrad import util
    server = SocketServer()
    util.runServer(server)
