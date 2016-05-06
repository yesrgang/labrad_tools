import numpy as np

class DACBoard(object):
    def __init__(self, **kwargs):
        """ defaults """
	self.bit_file = 'analog_sequencer.bit'
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
        self.name = '%LABRADNODE%_analog_sequencer'
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
                    DACChannel(loc='E06', name='HODT Intensity', mode='auto', manual_voltage=0),
                    DACChannel(loc='E07', name='VODT Intensity', mode='auto', manual_voltage=0),
                ],
            ),
            'F': DACBoard(
                device_id='srq analog 2',
                channels=[
                    DACChannel(loc='F00', name='Beta FM', mode='auto', manual_voltage=0),
                    DACChannel(loc='F01', name='813 H1 Intensity', mode='auto', manual_voltage=0),
                    DACChannel(loc='F02', name='813 H2 Intensity', mode='auto', manual_voltage=0),
                    DACChannel(loc='F03', name='813 V Intensity', mode='auto', manual_voltage=0),
                    DACChannel(loc='F04', name='Clock Intensity', mode='auto', manual_voltage=0),
                    DACChannel(loc='F05', name='813H mixer', mode='auto', manual_voltage=0),
                    DACChannel(loc='F06', name='813V mixer', mode='auto', manual_voltage=0),
                    DACChannel(loc='F07', name='Spin pol Intensity', mode='auto', manual_voltage=0),
                ],
            ),
            'G': DACBoard(
                device_id='srq analog 3',
                channels=[
                    DACChannel(loc='G00', name='DACG00', mode='auto', manual_voltage=0),
                    DACChannel(loc='G01', name='DACG01', mode='auto', manual_voltage=0),
                    DACChannel(loc='G02', name='DACG02', mode='auto', manual_voltage=0),
                    DACChannel(loc='G03', name='DACG03', mode='auto', manual_voltage=0),
                    DACChannel(loc='G04', name='DACG04', mode='auto', manual_voltage=0),
                    DACChannel(loc='G05', name='DACG05', mode='auto', manual_voltage=0),
                    DACChannel(loc='G06', name='DACG06', mode='auto', manual_voltage=0),
                    DACChannel(loc='G07', name='DACF07', mode='auto', manual_voltage=0),
                ],
            ),
        }
