from nf8742.nf8742 import NF8742

class VODTY(NF8742):
    socket_address = ('192.168.1.21', 23)
    controller_axis = 4

__device__ = VODTY
