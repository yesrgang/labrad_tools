import os
import time
from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def init_command(device):
    device['context'] = yield self.client.signal_generator.context()
    yield self.client.signal_generator.select_device_by_name('clock_steer', context=device['context'])

@inlineCallbacks
def update_command(device, value):
    yield self.client.signal_generator.frequency(value, context=device['context'])

config = {
    'clock_aom': {
        'frequency': {
            'init_command': init_command, 
            'update_command': update_command,
            'value': None,
        },
        'context': None,
    },
}

