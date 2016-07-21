from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def initialize(self):
    yield self.cxn.rf.select_device('clock_steer')

@inlineCallbacks
def update(self, value):
    yield self.cxn.rf.frequency(value)

config = {
    'clock_aom': {
        'frequency': {
            'initialize': initialize, 
            'update': update,
            'value': None,
        },
    },
}

