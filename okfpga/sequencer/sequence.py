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
    
    def __getitem__(self, key):
        return self.sequence[key] 

    def __iter__(self):
        return self.sequence.keys()

    def keys(self):
        return self.sequence.keys()

    def load(self, sequence):
        if type(sequence) == types.StringType:
            sequence = json.loads(sequence)
        if type(sequence) == types.DictType:
            self.sequence = sequence

    def dump(self):
        return json.dumps(self.sequence)

    def get_duration(self):
        return max([sum([d['dt'] for d in cs]) for cs in self.sequence.values()])
