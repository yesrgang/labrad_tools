from nf8742.nf8742 import NF8742

class H1YR(NF8742):
    socket_address = ('192.168.1.20', 23)
    controller_axis = 2

__device__ = H1YR
