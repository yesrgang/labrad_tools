import json
import os
import time

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
	self._record(data)
	returnValue(data)
    
    def _record(self, data):
        if self.do_record:
            self.data.append(data)
	    if len(self.data) > 1:
                print 'appending {}/{}'.format(len(self.data)-1, self.num_cycles)
            if len(self.data) >= self.num_cycles+1:
#                iteration = 2
#                while os.path.isfile(self.filename):
#                    name = self.filename.split('#')[0]
#    		    self.filename = name + '#{}'.format(iteration)
#		    iteration += 1
#                with open(self.filename, 'w+') as outfile:
#			json.dump(self.data[1:], outfile)
#                print 'done recording {}'.format(self.filename)
#    		self.data = []
                self._write()
    		self.do_record = False

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

        with open(filename, 'w+') as outfile:
		json.dump(self.data[1:], outfile)
    	self.data = []
	try:
            self.clinet.yesr9_beeper.beep()
	except:
            pass
        print 'data written to {}'.format(filename)
        

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
