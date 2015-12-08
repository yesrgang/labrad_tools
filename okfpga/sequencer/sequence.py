import types
import json
class Sequence(object):
    """
    sequence class for making it easier to manipulate sequences
    """
    def __init__(self, sequence):
        """
        sequence should be {channel_id: [{dt, params}]}
        """
        self.load(sequence)

    def load(self, sequence):
        if type(sequence) == types.StringType:
            sequence = json.loads(sequence)
        if type(sequence) == types.DictType:
            self.sequence = sequence

    def dump(self):
        return json.dumps(self.sequence)

    def __getitem__(self, key):
        return self.sequence[key] 

sequence = {'a@TTLA00': [{'dt': 1, 's': 0}, {'dt': 2, 's': 1}], 'b@TTLA01': [{'dt': 1, 's': 0}, {'dt': 2, 's': 1}]}

sequence = json.dumps(sequence)

s = Sequence(sequence)
print s.dump()
