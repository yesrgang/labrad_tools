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

	self.channels = {c.key: c for c in self.channels}
        
	self.name_to_key = {d['name']: k for k, d in self.channels.items()}

class DACChannel(object):
    def __init__(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
	self.key = name+'@'+loc

class SequencerConfig(object):
    def __init__(self):
        self.update_id = 698023
	self.mode = 'idle'
        self.boards = {
            'E': DACBoard(
                device_id='sr2 dac1',
                channels=[
                    DACChannel(loc='E00', name='Alpha Intensity', mode='auto', manual_voltage=0),
                    DACChannel(loc='E01', name='Beta Intensity', mode='auto', manual_voltage=0),
                    DACChannel(loc='E02', name='X Comp. Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E03', name='Y Comp. Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E04', name='Z Comp. Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E05', name='MOT Coil', mode='auto', manual_voltage=0),
                    DACChannel(loc='E06', name='HODT', mode='auto', manual_voltage=-10),
                    DACChannel(loc='E07', name='dimple', mode='auto', manual_voltage=-10),
		    ],
                 ),
            'D': DACBoard(
                device_id='srq analog 2',
                channels=[
                    DACChannel(loc='D00', name='DACD00', mode='auto', manual_voltage=0),
                    DACChannel(loc='D01', name='DACD01', mode='auto', manual_voltage=0),
                    DACChannel(loc='D02', name='DACD02', mode='auto', manual_voltage=0),
                    DACChannel(loc='D03', name='DACD03', mode='auto', manual_voltage=0),
                    DACChannel(loc='D04', name='DACD04', mode='auto', manual_voltage=0),
                    DACChannel(loc='D05', name='DACD05', mode='auto', manual_voltage=0),
                    DACChannel(loc='D06', name='DACD06', mode='auto', manual_voltage=0),
                    DACChannel(loc='D07', name='DACD07', mode='auto', manual_voltage=0),
		    ],
                ),
            }
	
#	self.channels = {}
#	for b in self.boards:
#            for k, c in b.channels.items():
#                self.channels[k] = c
