import numpy as np

VOLTAGE_RANGE = (-10., 10.)
DAC_BITS = 16

def time_to_ticks(clk, time):
    return  int(clk * time)

def voltage_to_signed(voltage, voltage_range=VOLTAGE_RANGE, dac_bits=DAC_BITS):
    min_voltage = min(voltage_range)
    max_voltage = max(voltage_range)
    voltage_span = float(max_voltage - min_voltage)
    voltage = sorted([-voltage_span, voltage, voltage_span])[1]
    return int(voltage / voltage_span * (2**dac_bits - 1))

def voltage_to_unsigned(voltage, voltage_range=VOLTAGE_RANGE, dac_bits=DAC_BITS):
    min_voltage = min(voltage_range)
    max_voltage = max(voltage_range)
    voltage_span = float(max_voltage - min_voltage)
    voltage = sorted([min_voltage, voltage, max_voltage])[1] - min_voltage
    return int(voltage / voltage_span * (2**dac_bits - 1))

#def ramp_rate(voltage_diff, ticks, dac_bits=DAC_BITS):
#    v = voltage_to_signed(voltage_diff)
#    t = ticks
#    signed_ramp_rate = int(v * 2.0**int(np.log2(t) - 1.0) / t)
#    if signed_ramp_rate > 0:
#        return signed_ramp_rate
#    else:
#        return signed_ramp_rate + 2**dac_bits
#
def ramp_rate(bits, ticks, dac_bits=DAC_BITS):
    if ticks <= 0:
        message = 'time {} [s] corresponds to {} {} [Hz] clock cycles'.format(time, ticks, clk)
        raise Exception(message)
    signed_ramp_rate = int(bits * 2.0**int(np.log2(ticks) - 1.0) / ticks)
    if signed_ramp_rate > 0:
        return signed_ramp_rate
    else:
        return signed_ramp_rate + 2**dac_bits
