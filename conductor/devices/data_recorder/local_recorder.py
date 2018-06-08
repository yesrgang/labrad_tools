from copy import deepcopy
import os
import json
import shutil
from time import time

from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callInThread
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

def deepish_copy(org):
    '''
    much, much faster than deepcopy, for a dict of the simple python types.
    '''
    out = dict().fromkeys(org)
    for k,v in org.iteritems():
        out[k] = deepcopy(v) #.copy()   # dicts, sets
#   :        try:
#   :            out[k] = deepcopy(v) #.copy()   # dicts, sets
#   :        except AttributeError:
#   :            try:
#   :                out[k] = v[:]   # lists, tuples, strings, unicode
#   :            except TypeError:
#   :                out[k] = v      # ints
    return out

class LocalRecorder(ConductorParameter):
    priority = 1
#    local_data_dir = 'C:\\Users\\Ye Lab\\Desktop\\data\\{}'
    local_data_dir = '/home/srgang/.local-data/{}'
    writing_data = False
    write_counts = 1
    current_count = 1    
    verbose = False
    

    @inlineCallbacks
    def update(self):
        yield None
        t0 = time()
        try:
            if self.conductor.data_path and not self.writing_data:
                self.writing_data = True
#                data_copy = deepcopy(self.conductor.data)
                filename = os.path.split(self.conductor.data_path)[-1]
                callInThread(self._save_data, filename)
        except Exception as e:
            print "Error writing data"
            print e
        finally:
            self.writing_data = False        
        if self.verbose:
            print 'record', time() - t0

    def _save_data(self, filename):
        data = deepish_copy(self.conductor.data)
        local_path = self.local_data_dir.format(filename)
        self.current_count -= 1
        if self.current_count <= 0 and self.conductor.data_path:
        
            with open(local_path, 'w') as outfile:
                json.dump(data, outfile, default=lambda x: None)
            self.current_count = self.write_counts
#        shutil.copyfile(local_path, self.conductor.data_path)


    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        pass
