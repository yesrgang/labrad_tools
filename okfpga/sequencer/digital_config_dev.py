class PulseBoardConfig(object):
    def __init__(self, **kwargs):
        """ defaults """
        self.bit_file = 'sequencer.bit'
        self.mode_nums = {'idle': 0, 'load': 1, 'run': 2}
        self.mode = 'idle'
        self.mode_wire = 0x00
        self.pipe_wire = 0x80
        self.channel_mode_wires = [0x01, 0x03, 0x05, 0x07]
        self.channel_stateinv_wires = [0x02, 0x04, 0x06, 0x08]
        self.clk_frequency = 50e6
        
        """ non-defaults """
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
#	self.channels = {c.key: c for c in self.channels}

class PulseChannelConfig(object):
    def __init__(self, **kwargs):
        self.name = None
        self.loc = None
        self.board='1'

        """ non-defaults """
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
        
        if self.name is None:
            raise Exception('channel name is unspecified')
        if self.loc is None:
            raise Exception('channel location is unspecified')
        
        self.key = self.name+'@'+self.loc

class TimingChannelConfig(object):
    def __init__(self, **kwargs):
        self.name = 'digital@T'
        self.dt_range = (1e-6, 30)

        """ non-defaults """
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])



class DigitalSequencerConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% Digital Sequencer Dev'
	self.update_id = 698024
	self.timing_channel = TimingChannelConfig()

        self.boards = {
            '1': PulseBoardConfig(
                device_id='Sr2 dev.',
                channels=[
                    PulseChannelConfig(loc='A00', name='3D MOT AOM', mode='auto', manual_state=0, invert=1),
                    PulseChannelConfig(loc='A01', name='3D MOT Shutter', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A02', name='Floures. AOM', mode='auto', manual_state=0, invert=1),
                    PulseChannelConfig(loc='A03', name='Floures. Shutter', mode='auto', manual_state=0, invert=1),
                    PulseChannelConfig(loc='A04', name='Abs. AOM', mode='auto', manual_state=0, invert=1),
                    PulseChannelConfig(loc='A05', name='Abs. Shutter', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A06', name='2D MOT Shutter', mode='auto', manual_state=0, invert=1),
                    PulseChannelConfig(loc='A07', name='Zeeman Shutter', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A08', name='AH Enable', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A09', name='AH Bottom Enable', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A10', name='V Camera Trig.', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A11', name='H Camera Trig', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A12', name='Dimple AOM', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A13', name='HODT AOM', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A14', name='VODT AOM', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='A15', name='Spec. Lock Enable', mode='manual', manual_state=0, invert=1),

                    PulseChannelConfig(loc='B00', name='Tickle Enable', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B01', name='TTLB01', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B02', name='TTLB02', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B03', name='TTLB03', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B04', name='TTLB04', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B05', name='TTLB05', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B06', name='TTLB06', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B07', name='TTLB07', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B08', name='TTLB08', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B09', name='TTLB09', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B10', name='TTLB10', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B11', name='TTLB11', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B12', name='TTLB12', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B13', name='TTLB13', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B14', name='TTLB14', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='B15', name='TTLB15', mode='auto', manual_state=0, invert=0),
                    
                    PulseChannelConfig(loc='C00', name='TTLC00', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C01', name='RM Gain Switch', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C02', name='TTLC02', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C03', name='TTLC03', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C04', name='TTLC04', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C05', name='TTLC05', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C06', name='TTLC06', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C07', name='TTLC07', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C08', name='TTLC08', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C09', name='TTLC09', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C10', name='TTLC10', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C11', name='TTLC11', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C12', name='TTLC12', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C13', name='TTLC13', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C14', name='TTLC14', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='C15', name='TTLC15', mode='auto', manual_state=0, invert=0),
                    
                    PulseChannelConfig(loc='D00', name='Alpha AOM', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D01', name='Alpha Shutter', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D02', name='Beta AOM', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D03', name='Beta Shutter', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D04', name='Spin Pol. AOM', mode='auto', manual_state=0, invert=1),
                    PulseChannelConfig(loc='D05', name='Spin Pol. Shutter', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D06', name='679 AOM', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D07', name='707 AOM', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D08', name='Repump Shutter', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D09', name='TTLD09', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D10', name='TTLD10', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D11', name='TTLD11', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D12', name='TTLD12', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D13', name='TTLD13', mode='auto', manual_state=0, invert=0),
                    PulseChannelConfig(loc='D14', name='AOSense Heater Enable', mode='manual', manual_state=1, invert=0),
                    PulseChannelConfig(loc='D15', name='Trigger', mode='auto', manual_state=0, invert=0),
                    ]
                ),
            }
