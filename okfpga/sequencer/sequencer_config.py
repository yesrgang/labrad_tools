class SequencerConfig(object):
    def __init__(self):
        self.bit_file = 'sequencer.bit'
        self.sequencer_mode_num = {'idle': 0, 'load': 1, 'run': 2}
        self.sequencer_mode = 'idle'
        self.channel_mode_wires = [0x01, 0x03, 0x05, 0x07]
        self.channel_stateinv_wires = [0x02, 0x04, 0x06, 0x08]
        self.clk_frequency = 50e6
        self.okDeviceID = 'Sr2 dev.'

        """
        channels is a dictionary for all channels.
        keys get mapped to physical channels through sorted(). should be kept same as labels on the sequencer box.
        the dictionary returns another dictionary with configuration parameters:
            'name' can be any string
            'mode' is 'auto' or 'manual'
            'manual state' is bool
            'invert' is bool, is "on" hi or lo?
        """
        self.channels = {
                        'A00': {'name': '3D MOT AOM', 'mode': 'auto', 'manual state': 0, 'invert': 1},
                        'A01': {'name': '3D MOT Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A02': {'name': 'Fluores. AOM', 'mode': 'auto', 'manual state': 0, 'invert': 1},
                        'A03': {'name': 'Fluores. Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
                        'A04': {'name': 'Abs. AOM', 'mode': 'auto', 'manual state': 0, 'invert': 1},
                        'A05': {'name': 'Abs. Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
                        'A06': {'name': 'TC Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
                        'A07': {'name': 'Zeeman Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
                        'A08': {'name': 'TTLA08', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A09': {'name': 'TTLA09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A10': {'name': 'TTLA10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A11': {'name': 'TTLA11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A12': {'name': 'TTLA12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A13': {'name': 'TTLA13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A14': {'name': 'TTLA14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'A15': {'name': 'TTLA15', 'mode': 'auto', 'manual state': 0, 'invert': 0},

                        'B00': {'name': 'TTLB00', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B01': {'name': 'TTLB01', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B02': {'name': 'TTLB02', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B03': {'name': 'TTLB03', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B04': {'name': 'TTLB04', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B05': {'name': 'TTLB05', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B06': {'name': 'TTLB06', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B07': {'name': 'TTLB07', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B08': {'name': 'TTLB08', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B09': {'name': 'TTLB09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B10': {'name': 'TTLB10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B11': {'name': 'TTLB11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B12': {'name': 'TTLB12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B13': {'name': 'TTLB13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B14': {'name': 'TTLB14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'B15': {'name': 'TTLB15', 'mode': 'auto', 'manual state': 0, 'invert': 0},

                        'C00': {'name': 'TTLC00', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C01': {'name': 'TTLC01', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C02': {'name': 'TTLC02', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C03': {'name': 'TTLC03', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C04': {'name': 'TTLC04', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C05': {'name': 'TTLC05', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C06': {'name': 'TTLC06', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C07': {'name': 'TTLC07', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C08': {'name': 'TTLC08', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C09': {'name': 'TTLC09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C10': {'name': 'TTLC10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C11': {'name': 'TTLC11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C12': {'name': 'TTLC12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C13': {'name': 'TTLC13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C14': {'name': 'TTLC14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'C15': {'name': 'TTLC15', 'mode': 'auto', 'manual state': 0, 'invert': 0},

                        'D00': {'name': 'Alpha AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D01': {'name': 'Alpha Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D02': {'name': 'Beta AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D03': {'name': 'Beta Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D04': {'name': 'Spin pol. AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D05': {'name': 'Spin pol. Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D06': {'name': '679 AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D07': {'name': '707 AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D08': {'name': 'Repump Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D09': {'name': 'TTLD09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D10': {'name': 'TTLD10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D11': {'name': 'TTLD11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D12': {'name': 'TTLD12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D13': {'name': 'TTLD13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D14': {'name': 'TTLD14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        'D15': {'name': 'TTLD15', 'mode': 'auto', 'manual state': 0, 'invert': 0},
                        }

        self.name_to_key = {d['name']: k for k, d in self.channels.items()}
