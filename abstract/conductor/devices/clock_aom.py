import os
import time
from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def init_command(device):
    device['frequency']['context'] = yield self.client.signal_generator.context()
    context = device['frequency']['context']
    yield self.client.signal_generator.select_device_by_name('clock_steer', context=context)

@inlineCallbacks
def update_command(device, value):
    context = device['frequency']['context']
    yield self.client.signal_generator.frequency(value, context=context)

config = {
    'clock_aom': {
        'frequency': {
            'init_command': init_command, 
            'update_command': update_command,
            'context': None,
            'value': None,
        },
    },
}

