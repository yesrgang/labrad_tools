from devices.solstis.solstis import Solstis

class M2Sprout(Solstis):
    socket_address = ('128.138.107.141', 39933)
    socket_timeout = 1

__device__ = M2Sprout
