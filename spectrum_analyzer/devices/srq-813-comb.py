from devices.dsa815.dsa815 import DSA815

class SA(DSA815):
    vxi11_address = '192.168.1.8'
    trace_index = 1

__device__ = SA
