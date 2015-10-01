import numpy as np

class SequencerConfig(object):
    def __init__(self):
        self.update_id = 698023
        self.okDeviceID = 'srq analog 2'
        self.bit_file = 'dac_glitchfix2.bit'
        self.sequencer_mode_num = {'idle': 0, 'load': 1, 'run': 2}
        self.sequencer_mode = 'idle'
	self.channel_mode_wire = 0x09
        self.manual_voltage_wires = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        self.clk_frequency = 48e6 / (8.*2. + 2.)
        self.ramps = {
                     'linear': linear_ramp,
                     'exp': exp_ramp,
                     }

        """
        channels is a dictionary for all channels.
        keys get mapped to physical channels through sorted(). should be kept same as labels on the sequencer box.
        the dictionary returns another dictionary with configuration parameters:
            'name' can be any string
            'mode' is 'auto' or 'manual'
            'manual voltage' is number in Volts [-10, 10]
        """
        self.channels = {
                        'E08': {'name': 'DACE08', 'mode': 'auto', 'manual voltage': 0},
                        'E09': {'name': 'DACE09', 'mode': 'auto', 'manual voltage': 0},
                        'E10': {'name': 'DACE10', 'mode': 'auto', 'manual voltage': 0},
                        'E11': {'name': 'DACE11', 'mode': 'auto', 'manual voltage': 0},
                        'E12': {'name': 'DACE12', 'mode': 'auto', 'manual voltage': 0},
                        'E13': {'name': 'DACE13', 'mode': 'auto', 'manual voltage': 0},
                        'E14': {'name': 'DACE14', 'mode': 'auto', 'manual voltage': 0},
                        'E15': {'name': 'DACE15', 'mode': 'auto', 'manual voltage': 0},
                        }

        self.name_to_key = {d['name']: k for k, d in self.channels.items()}

def linear_ramp(p):
    return [p['t']], [p['vf']]

def exp_ramp(p):
    a = (p['vf'] - p['vi']) / (np.exp(p['t']/p['tau']) - 1)
    c = p['vi'] - a
    continuous = lambda t: a * np.exp(t/p['tau']) + c
    T = np.linspace(0, p['t'], p['pts']+1)
    dT = [self.p['t']/float(p['pts'])]*p['pts']
    V = continuous(T)
    V[-1] = p['vf']
    return dT, V[1:]



