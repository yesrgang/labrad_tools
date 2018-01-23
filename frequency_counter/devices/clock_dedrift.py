from devices.ag53220a.ag53220a import AG53220A

class ClockDedrift(AG53220A):
    vxi11_address = '192.168.1.13'
    channel = 1

__device__ = ClockDedrift
