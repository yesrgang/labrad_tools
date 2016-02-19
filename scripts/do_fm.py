import labrad
import time
cxn = labrad.connect()
bus20 = cxn.yesr20_gpib_bus

COUNTER_ADDRESS = 'GPIB0::23'
GENERATOR_ADDRESS = 'GPIB0::25'

def set_ramprate(ramprate):
    T_ramp = 8e3
    bus20.address('GPIB0::23')
    current_frequency = 29e6
    current_frequency = float(bus20.query('MEAS:FREQ? DEF, DEF, (@1)'))
    print current_frequency
    bus20.address('GPIB0::25')
    bus20.write('SOUR1:FUNCtion SIN')
    bus20.write('SOUR1:FREQ {}'.format(current_frequency))
    bus20.write('SOUR1:FREQ:STAR {}'.format(current_frequency))
    stop_frequency = current_frequency + ramprate*T_ramp
    print stop_frequency
    bus20.write('SOUR1:FREQ:STOP {}'.format(stop_frequency))
    bus20.write('SOUR1:SWEEp:TIME {}'.format(T_ramp))
    bus20.write('SOUR1:VOLT 500e-3')
    bus20.write('SOUR1:VOLT:OFFS 0')
    bus20.write('TRIG1:SOUR IMM')
    bus20.write('SOUR1:FREQ:MODE SWE')
    bus20.write('OUTP 1')

def set_frequency(frequency):
    bus20.address(GENERATOR_ADDRESS)
    bus20.write('SOUR2:FUNCtion SIN')
    bus20.write('SOUR2:VOLT 500e-3')
    bus20.write('SOUR2:VOLT:OFFS 0')
    bus20.write('SOUR2:FREQ {}'.format(frequency))
    bus20.write('OUTP2 1')


#set_frequency(27.115e6)
set_ramprate(18.6e-3 )




