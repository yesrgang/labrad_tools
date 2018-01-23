from nf8742.nf8742 import NF8742

class H1X(NF8742):
    socket_address = ('192.168.1.12', 23)
    controller_axis = 3

__device__ = H1X
