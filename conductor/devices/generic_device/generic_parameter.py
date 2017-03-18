from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

class GenericParameter(object):
    """ base class for conductor devices

    GP.initialize gets called only once on loading device into conductor.
        use to initialize labrad connection and configure device.

    GP.update gets called at begining of every experimental cycle.
        use to send value to hardware.

    GP.value should return a generic object (usually just a float) representing the device's "value"
        for the current run of the experiment.
        GP.value is set to <value> in conductor with "GP.value = <value>"
        Each experimental cycle, conductor saves output of value to data 

    GP.advance should advance to next queued value or if no queued values, keeps current value.
    
    GP.remaining_points should give int number of values in queue.
    
    since value can be anything, we specify value_type to make sure advance/remaining_points 
        have correct behavior.
        value_type = 'single':
            default. if _value is list, pops/returns first value in list
            else returns _value.
        
        value_type = 'list':
            a single value is a list
            if _value is list of lists, pops/returns first item
            else returns _value.

        value_type = 'once':
            _value is anything. 
            returns _value then sets _value to None

        value_type = 'data':
            _value is anything
            remaining_points = None
            returns _value

    """
    priority = 1
    value_type = 'single'

    def __init__(self, config):
        self._value = None
        for key, value in config.items():
            setattr(self, key, value)

    @inlineCallbacks
    def initialize(self):
        yield None
    
    @inlineCallbacks
    def update(self):
        yield None

    @inlineCallbacks
    def stop(self):
        yield None

    @property
    def value(self):
        if self.value_type == 'single':
            if type(self._value).__name__ == 'list':
                return self._value[0]
            else:
                return self._value
        elif self.value_type == 'list':
            if self._value:
                if type(self._value[0]).__name__ == 'list':
                    return self._value[0]
                else:
                    return self._value
        elif self.value_type == 'once':
            return self._value
        elif self.value_type == 'data':
            return self._value
        else:
            return None

    @value.setter
    def value(self, value):
        self._value = value
    
    def advance(self):
        if self.value_type == 'single':
            if type(self._value).__name__ == 'list':
                old = self._value.pop(0)
                if not len(self._value):
                    self.value = old
        elif self.value_type == 'list':
            if self._value:
                if type(self._value[0]).__name__ == 'list':
                    old = self._value.pop(0)
                    if not len(self._value):
                        self.value = old
        elif self.value_type == 'once':
            self._value = None

    def remaining_values(self):
        if self.priority:
            if self.value_type == 'single':
                if type(self._value).__name__ == 'list':
                    return len(self._value) - 1
            if self.value_type == 'list':
                if self._value:
                    if type(self._value[0]).__name__ == 'list':
                        return len(self._value) - 1

