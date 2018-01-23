from devices.dsa815.dsa815 import DSA815

class SA(DSA815):
    vxi11_address = '128.138.107.81'
    trace_index = 1

__device__ = SA
