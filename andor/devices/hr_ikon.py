from devices.ikon.ikon import Ikon

class HRIkon(Ikon):
    autostart = True
    
    # andor api settings
    fan_mode = 2
    temperature = -80
    cooler_mode = 0
    cooler_on = 1
    read_mode = 4
    shutter_type = 1
    shutter_mode = 1
    shutter_closing_time = 0
    shutter_opening_time = 0
    trigger_mode = 1
    accumulation_cycle_time = 0
    number_accumulations = 1
    kinetic_cycle_time = 0
    pre_amp_gain = 0
    hs_speed_type = 0
    hs_speed_index = 0
    vs_speed_index = 1

__device__ = HRIkon
