import labrad
import json

cxn = labrad.connect()
aseq2 = cxn.yesr20_analog_sequencer_2
channels = aseq2.get_channels()
channels = eval(channels)
seq0 = [(1, dict([(name, {'type': 'linear', 'v': 0}) for name in channels.values()]))]
seq0 = [(1, dict([(name, {'type': 'linear', 'v': 1}) for name in channels.values()]))]
seq = seq1 + seq0
seq = seq*30
aseq2.run_sequence(json.dumps(seq))


