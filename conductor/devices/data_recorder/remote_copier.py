from copy import deepcopy
import os
import time
import json
import shutil

from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callInThread
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class RemoteCopier(ConductorParameter):
    priority = 1
    local_data_dir = 'C:\\Users\\Ye Lab\\Desktop\\data\\{}'
    copy_counts = 1
    current_count = 1

    @inlineCallbacks
    def update(self):
        yield None
        self.current_count -= 1
        if self.current_count <= 0 and self.conductor.data_path:
            filename = os.path.split(self.conductor.data_path)[-1]
            local_path = self.local_data_dir.format(filename)
            if os.path.exists(local_path):
                shutil.copyfile(local_path, self.conductor.data_path)
            self.current_count = self.copy_counts

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        pass
