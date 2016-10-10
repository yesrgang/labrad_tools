from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

class GenericParameter(object):
    priority = 0
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
            if type(self._value[0]).__name__ == 'list':
                return self._value[0]
            else:
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
                if len(self._value) <= 1:
                    self.value = old
        if self.value_type == 'list':
            if type(self._value[0]).__name__ == 'list':
                old = self._value.pop(0)
                if len(self._value) <= 1:
                    self.value = old

    def remaining_values(self):
        if self.priority:
            if self.value_type == 'single':
                if type(self._value).__name__ == 'list':
                    return len(self._value)
            if self.value_type == 'list':
                if type(self._value[0]).__name__ == 'list':
                    return len(self._value)

