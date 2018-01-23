import json

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

from msquared import MSquared

class Solstis(MSquared):
    etalon_tune = 0.
    resonator_tune = 0.
    resonator_fine_tune = 0.

    @inlineCallbacks
    def set_system_status(self, value):
        yield None

    @inlineCallbacks
    def get_system_status(self):
        response = yield self.get('get_status')
        if response:
            for key, value in response.iteritems():
                if (value == 'off'): 
                    response[key] = False
                if (value == 'on'): 
                    response[key] = True
            returnValue(json.dumps(response))
        else:
            returnValue(json.dumps({}))
    
    @inlineCallbacks
    def set_etalon_lock(self, value):
        yield self.set('etalon_lock', 
                       'on' if value else 'off', 
                       key_name='operation')

    @inlineCallbacks
    def get_etalon_lock(self):
        response = yield self.get('etalon_lock_status')
        if response:
            returnValue(response['condition'] == 'on')
        else:
            returnValue(False)
    
    @inlineCallbacks
    def set_etalon_tune(self, value):
        percentage = sorted([0., float(value), 100.])[1]
        yield self.set('tune_etalon', percentage)
        self.etalon_tune = percentage

    @inlineCallbacks
    def get_etalon_tune(self):
        yield None
        returnValue(self.etalon_tune)
    
    @inlineCallbacks
    def set_resonator_tune(self, value):
        percentage = sorted([0., float(value), 100.])[1]
        yield self.set('tune_resonator', percentage)
        self.resonator_tune = percentage

    @inlineCallbacks
    def get_resonator_tune(self):
        yield None
        returnValue(self.resonator_tune)

    @inlineCallbacks
    def set_resonator_fine_tune(self, value):
        percentage = sorted([0., float(value), 100.])[1]
        yield self.set('fine_tune_etalon', percentage)
        self.resonator_fine_tune = percentage

    @inlineCallbacks
    def get_resonator_fine_tune(self):
        yield None
        returnValue(self.resonator_fine_tune)

