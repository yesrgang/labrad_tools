from devices.dsa815.dsa815 import DSA815

class RedMOT(DSA815):
    vxi11_address = '192.168.1.4'
    trace_index = 1

__device__ = RedMOT
