class SequencerConfig(object):
    def __init__(self):
        self.bit_file = 'dac.bit'
        self.mode_num = {'idle': 0, 'load': 1, 'run': 2}

        self.channels = {
                        'A00': 'TTL00',
                        'A01': 'TTL01',
                        'A02': 'TTL02',
                        'A03': 'TTL03',
                        'A04': 'TTL04',
                        'A05': 'TTL05',
                        'A06': 'TTL06',
                        'A07': 'TTL07',
                        'A08': 'TTL08',
                        'A09': 'TTL09',
                        'A10': 'TTL10',
                        'A11': 'TTL11',
                        'A12': 'TTL12',
                        'A13': 'TTL13',
                        'A14': 'TTL14',
                        'A15': 'TTL15',
                        'A16': 'TTL16',
                        'A17': 'TTL17',
                        }
