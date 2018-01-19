from copy import deepcopy
import os
import time
import json
import shutil

from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callInThread
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class LocalRecorder(ConductorParameter):
    priority = 1
    local_data_dir = 'C:\\Users\\Ye Lab\\Desktop\\data\\{}'
    writing_data = False

    @inlineCallbacks
    def update(self):
        yield None
        try:
            if self.conductor.data_path and not self.writing_data:
                self.writing_data = True
                data_copy = deepcopy(self.conductor.data)
                filename = os.path.split(self.conductor.data_path)[-1]
                callInThread(self._save_data, data_copy, filename)
        except Exception as e:
            print "Error writing data"
            print e
        finally:
            self.writing_data = False        

    def _save_data(self, data, filename):
        local_path = self.local_data_dir.format(filename)
        with open(local_path, 'w') as outfile:
            json.dump(data, outfile, default=lambda x: None)
#        shutil.copyfile(local_path, self.conductor.data_path)


    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        pass
