import numpy as np

class SequencerConfig(object):
    def __init__(self):
        self.okDeviceID = 'sr2 dac1'
        self.bit_file = 'dac_trigger_glitchfix.bit'
        self.sequencer_mode_num = {'idle': 0, 'load': 1, 'run': 2}
        self.sequencer_mode = 'idle'
#        self.channel_mode_wires = [0x01, 0x03, 0x05, 0x07]
#        self.channel_stateinv_wires = [0x02, 0x04, 0x06, 0x08]
        self.clk_frequency = 10e6 / (8.*2. + 2.)
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
                        'E00': {'name': 'Alpha Intensity', 'mode': 'auto', 'manual voltage': 0},
                        'E01': {'name': 'Beta Intensity', 'mode': 'auto', 'manual voltage': 0},
                        'E02': {'name': 'DACA02', 'mode': 'auto', 'manual voltage': 0},
                        'E03': {'name': 'DACA03', 'mode': 'auto', 'manual voltage': 0},
                        'E04': {'name': 'DACA04', 'mode': 'auto', 'manual voltage': 0},
                        'E05': {'name': 'DACA05', 'mode': 'auto', 'manual voltage': 0},
                        'E06': {'name': 'DACA06', 'mode': 'auto', 'manual voltage': 0},
                        'E07': {'name': 'DACA07', 'mode': 'auto', 'manual voltage': 0},
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



