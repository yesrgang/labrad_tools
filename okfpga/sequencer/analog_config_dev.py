import numpy as np

class DACBoard(object):
    def __init__(self, **kwargs):
        """ defaults """
	self.bit_file = 'dac_glitchfix2.bit'
	self.mode_nums = {'idle': 0, 'load': 1, 'run': 2}
	self.mode = 'idle'
	self.mode_wire = 0x00
	self.channel_mode_wire = 0x09
	self.manual_voltage_wires = {'00': 0x01, '01': 0x02, '02': 0x03, '03': 0x04, 
                                     '04': 0x05, '05': 0x06, '06': 0x07, '07': 0x08}
        self.clk_frequency = 48e6 / (8.*2. + 2.)
        """ non-defaults """
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
#	self.channels = {c.key: c for c in self.channels}

class DACChannel(object):
    def __init__(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
	self.key = self.name+'@'+self.loc

class AnalogSequencerConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% Analog Sequencer Dev'
        self.update_id = 698023
	self.mode = 'idle'
        self.boards = {
            'E': DACBoard(
                device_id='sr2 dac1',
                channels=[
                    DACChannel(loc='E00', name='Alpha Intensity', mode='auto', manual_voltage=10),
                    DACChannel(loc='E01', name='Beta Intensity', mode='auto', manual_voltage=10),
                    DACChannel(loc='E02', name='X Comp. Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E03', name='Y Comp. Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E04', name='Z Comp. Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E05', name='MOT Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E06', name='DACE06', mode='auto', manual_voltage=0),
                    DACChannel(loc='E07', name='DACE07', mode='auto', manual_voltage=0),
		    ],
                 ),
            'F': DACBoard(
                device_id='srq analog 2',
                channels=[
                    DACChannel(loc='F00', name='DACF00', mode='auto', manual_voltage=0),
                    DACChannel(loc='F01', name='DACF01', mode='auto', manual_voltage=0),
                    DACChannel(loc='F02', name='DACF02', mode='auto', manual_voltage=0),
                    DACChannel(loc='F03', name='DACF03', mode='auto', manual_voltage=0),
                    DACChannel(loc='F04', name='DACF04', mode='auto', manual_voltage=0),
                    DACChannel(loc='F05', name='DACF05', mode='auto', manual_voltage=0),
                    DACChannel(loc='F06', name='DACF06', mode='auto', manual_voltage=0),
                    DACChannel(loc='F07', name='DACF07', mode='auto', manual_voltage=0),
		    ],
                ),
            }

#	self.ramps = {'lin': lin_ramp, 'exp': exp_ramp}

#def lin_ramp(s):
#    T, loc, p = s
#    dv = p['vf'] - p['vi']
#    return [(T, loc, {'dv': dv, 'dt': p['dt']})]
#
#def exp_ramp(s):
#    T, loc, p = s
#    a = (p['vf'] - p['vi']) / (np.exp(-p['dt']/p['tau']) - 1)
#    c = p['vi'] - a
#    continuous = lambda t: a*np.exp(-t/p['tau']) + c
#    t_pts = np.linspace(0, p['dt'], p['pts']+1)
#    dt = p['dt']/float(p['pts'])
#    V = continuous(t_pts)
#    dV = [V[i+1]-V[i] for i in range(p['pts'])]
#    return [(T+tp, loc, {'dv': dv, 'dt': dt}) for tp, dv in zip(t_pts[:-1], dV)]
#
