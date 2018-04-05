from sg382.sg382 import SG382

class ClockSteer(SG382):
    vxi11_address = "192.168.1.29"
    
    frequency_range = (20e3, 30e6)

__device__ = ClockSteer
