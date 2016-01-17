import json
import os
import time
import types

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

class ReceiverServer(LabradServer):
    name = '%LABRADNODE% Receiver'
    data = []
    do_record = False
    
    @setting(1, 'send string', string='s', returns='s')
    def send_string(self, c, string):
        data = {}
        analysis = json.loads(string[1:-1].replace("'",'"'))
        data['analysis'] = analysis
        params = yield self.client.yesr20_conductor.get_previous_parameters()
        data['parameters'] = json.loads(params)
        yield self._record(data)
        returnValue(data)
    
    @inlineCallbacks 
    def _record(self, data):
        if self.do_record:
            self.data.append(data)
        if len(self.data) > 1:
            print 'appending {}/{}'.format(len(self.data)-1, self.num_cycles)
        if len(self.data) >= self.num_cycles+1:
            yield self._write()
    	    self.do_record = False
        else:
            yield None

    @inlineCallbacks
    def _write(self):
        # write file to todays data folder
        data_dir = 'Z:\\SrQ\\data\\'
        todays_dir = data_dir + time.strftime('%Y%m%d')
        if not os.path.exists(todays_dir):
            os.mkdir(todays_dir)
        
        # append experiment run number
        filename = todays_dir + '\\' + self.filename + '#0'
        iteration = 0
        while os.path.isfile(filename):
            filename = filename.split('#')[0] + '#{}'.format(iteration)
            iteration += 1

        # data [{}] -> {[]}
        cdata = self._compact_data(self.data[1:])

        # add in sequence
        sequence = yield self.client.yesr20_conductor.get_sequence()
        cdata['sequence'] = json.loads(sequence)

        with open(filename, 'w+') as outfile:
            json.dump(cdata, outfile)
        self.data = []
        
        # try to beep
        try:
            yield self.client.yesr9_beeper.beep()
        except:
            print 'no beep'
        
        print 'data written to {}'.format(filename)

    def _compact_data(self, data_list):
        if type(data_list[0]) == types.DictType:
            return {k: self._compact_data([d[k] for d in data_list]) for k in data_list[0].keys()}
        else:
            return data_list

    @setting(2, 'record', filename='s', num_cycles='i')
    def record(self, c, filename, num_cycles):
        print 'starting record {} points'.format(num_cycles)
        self.data = []
        self.filename = filename
        self.num_cycles = num_cycles
        self.do_record = True

    @setting(3, 'stop record', do_write='b')
    def stop_record(self, c, do_write=True):
        self.do_record = False
        if do_write:
            self._write()

if __name__ == "__main__":
    __server__ = ReceiverServer()
    from labrad import util
    util.runServer(__server__)
