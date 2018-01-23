from devices.solstis.solstis import Solstis

class M2Verdi(Solstis):
    socket_address = ('128.138.107.135', 39933)
    socket_timeout = 1

__device__ = M2Verdi
