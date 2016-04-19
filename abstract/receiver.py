"""
### BEGIN NODE INFO
[info]
name = receiver
version = 1.0
description = 
instancename = %LABRADNODE%_receiver

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json
import os
import time
import types
import numpy as np

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

class ReceiverServer(LabradServer):
    name = '%LABRADNODE%_receiver'
    data = []
    do_record = False
    num_cycles = 0
    display = ''
    
    @setting(1, 'send string', string='s', returns='s')
    def send_string(self, c, string):
        data = {}
        analysis = json.loads(string[1:-1].replace("'",'"'))
        data['analysis'] = analysis
#        print analysis
        params = yield self.client.yesr20_conductor.get_previous_parameters()
        data['parameters'] = json.loads(params)
        data['timestamp'] = time.time()
        yield self._record(data)
#        print data
        returnValue(data)
    
    @inlineCallbacks 
    def _record(self, data):
        if self.do_record:
            self.data.append(data)
        if len(self.data) > 1:
            print 'appending {}/{}'.format(len(self.data)-1, self.num_cycles)
            yield self._write()
        if len(self.data) >= self.num_cycles+1:
            print 'data written to {}'.format(self.filename)
            self.data = []
    	    self.do_record = False
        else:
            yield None

    @inlineCallbacks
    def _write(self):
        # data [{}] -> {[]}
        cdata = self._compact_data(self.data[1:])

        # add in sequence
        sequence = yield self.client.yesr20_conductor.get_sequence()
        cdata['sequence'] = json.loads(sequence)

        with open(self.filename, 'w+') as outfile:
            json.dump(cdata, outfile)

    @inlineCallbacks
    def _beep(self):
        try:
            yield self.client.yesr13_beeper.beep()
        except:
            print 'no beep'

    def _set_filename(self, filename):
        # write file to todays data folder
        data_dir = 'Z:\\SrQ\\data\\'
        todays_dir = data_dir + time.strftime('%Y%m%d')
        if not os.path.exists(todays_dir):
            os.mkdir(todays_dir)
        
        # append experiment run number
        self.filename = todays_dir + '\\' + filename + '#0'
        iteration = 0
        while os.path.isfile(self.filename):
            self.filename = self.filename.split('#')[0] + '#{}'.format(iteration)
            iteration += 1


    def _compact_data(self, data_list):
        if type(data_list[0]) == types.DictType:
            return {k: self._compact_data([d[k] for d in data_list]) for k in data_list[0].keys()}
        else:
            return data_list

    @setting(2, 'record', filename='s', num_cycles='i')
    def record(self, c, filename, num_cycles):
        print 'starting record {} points'.format(num_cycles)
        self.data = []
        self._set_filename(filename)
        print 'saving data to {}'.format(self.filename)
        self.num_cycles = num_cycles
        self.do_record = True

    @setting(3, 'stop record', do_write='b')
    def stop_record(self, c, do_write=True):
        self.do_record = False
        if do_write:
            self._write()

    @setting(4, 'send gage', string='s')
    def send_gage(self, c, string):
        data = {}
        analysis = json.loads(string)
        data['analysis'] = analysis
        params = yield self.client.yesr20_conductor.get_previous_parameters()
        data['parameters'] = json.loads(params)
        data['timestamp'] = time.time()
        yield self._record(data)
        if self.display:
            bac = np.array(analysis['bac'])
            gnd = np.array(analysis['gnd']) - bac
            exc = np.array(analysis['exc']) - bac
            print exc / (gnd + exc)

    @setting(5, 'set display', display='s')
    def set_display(self, c, display):
        self.display = display

if __name__ == "__main__":
    __server__ = ReceiverServer()
    from labrad import util
    util.runServer(__server__)
