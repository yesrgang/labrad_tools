from copy import deepcopy
import os
import time
import json
import shutil

from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callInThread
from labrad.wrappers import connectAsync
from time import time

from conductor_device.conductor_parameter import ConductorParameter

class RemoteCopier(ConductorParameter):
    priority = 1
    local_data_dir = '/home/srgang/.local-data/{}'
    copy_counts = 1
    current_count = 1
    verbose = False

    @inlineCallbacks
    def update(self):
        yield None
        t0 = time()
        self.current_count -= 1
        if self.current_count <= 0 and self.conductor.data_path:
            filename = os.path.split(self.conductor.data_path)[-1]
            local_path = self.local_data_dir.format(filename)
            if os.path.exists(local_path):
                shutil.copyfile(local_path, self.conductor.data_path)
            self.current_count = self.copy_counts
        if self.verbose:
            print 'copy', time() - t0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        pass
