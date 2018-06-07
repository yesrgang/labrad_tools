import afg3252.afg3252
reload(afg3252.afg3252)
from afg3252.afg3252 import AFG3252

class ClockFiberDemod(AFG3252):
    visa_server_name = 'yesr5_gpib'
    visa_address = 'USB0::0x0699::0x0345::C020003::INSTR' 
    source = 1
    
#    frequency_range = (1, 240e6)

__device__ = ClockFiberDemod
