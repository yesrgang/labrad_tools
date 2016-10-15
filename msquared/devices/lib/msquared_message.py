import json

from numpy import random

class MSquaredMessage(object):
    def __init__(self, op, parameters, transmission_id=False):
        self.op = op
        self.parameters = parameters
        if (transmission_id):
            self.transmission_id = transmission_id
        else:
            self.transmission_id = random.randint(1, 999)

    @classmethod
    def from_json(cls, json_string):
        msg = json.loads(json_string)['message']
        op = msg['op']
        parameters = msg['parameters']
        transmission_id = msg['transmission_id'][0]
        return cls(op, parameters, transmission_id)

    def message(self):
        m = {
            'transmission_id': [self.transmission_id],
            'op': self.op,
            'parameters': self.parameters
        }
        if self.parameters == None: 
            del m['parameters']
        return m

    def to_json(self):
        return json.dumps({'message': self.message()})

    def is_ok(self, status='ok'):
        if 'status' in self.parameters:
            return self.parameters['status'] == status
        else:
            return None

    def __repr__(self):
        return '<MSquaredMessage transmission_id=%s op=%s parameters=%s>' % \
                (str(self.transmission_id), self.op, str(self.parameters))
