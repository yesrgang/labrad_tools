from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def initialize_stepper_motor(self):
    yield self.cxn.stepper_motor.select_device('nd_filter')

@inlineCallbacks
def update_stepper_motor(self, value):
    yield self.cxn.stepper_motor.move_absolute(value)

config = {
    'position': {
        'initialize': initialize_stepper_motor,
        'update': update_stepper_motor,
        'value': 2200,
    },
},
