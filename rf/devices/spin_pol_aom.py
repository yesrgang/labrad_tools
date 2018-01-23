from devices.ds345.ds345 import DS345

class SpinPolAOM(DS345):
    gpib_server_name = 'yesr9_gpib'
    gpib_address = 'GPIB0::21::INSTR'

__device__ = SpinPolAOM
