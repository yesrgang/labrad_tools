from labrad.wrappers import connectAsync
import sys
from twisted.internet.defer import inlineCallbacks
import json
import re
import numpy as np
sys.path.append('../')
from conductor_device.conductor_parameter import ConductorParameter

# calibration
def res2tmp(r):
    a0 = 82.909771771
    a1 = -0.0026491017
    a2 = 5.42885866e-8
    a3 = -6.997041909e-13
    a4 = 4.932318795e-18
    a5 = -1.45274715887e-23
    return a5*r**5+a4*r**4+a3*r**3+a2*r**2+a1*r+a0


class KeithleyTemperature(ConductorParameter):

    value_type = 'single'

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
#        yield self.cxn.yesr11_socket.connect(('192.168.1.2', 1394))
    
    @inlineCallbacks
    def update(self):
        yield self.cxn.yesr11_socket.connect(('192.168.1.2', 1394))
        yield self.cxn.yesr11_socket.send('TRAC:DATA?\n')
        ans = yield self.cxn.yesr11_socket.recv(4096)
        yield self.cxn.yesr11_socket.close()
        prog = re.compile('(?P<reading>[\w.+]+),(?P<time>[\w:.]+),(?P<date>[\w-]+),(?P<channel>[\d]+),(?P<limits>[\d]+)')

        t_ = []
        ch_ = []
        for m in prog.finditer(ans):
            t_.append(res2tmp(float(m.group('reading'))))
            ch_.append(int(m.group('channel')))

        sch = range(101, 109)
        st_ = {}

        for j in range(0, len(sch)):
            ind_ = []
            for i in range(0, len(ch_)):
                if ch_[i] == sch[j]:
                    ind_.append(i)
            st_[str(sch[j])] = t_[ind_[0]]
#        print st_

        self.value = st_
        values = json.dumps({'temperature': st_})
#        print values
        yield self.cxn.conductor.set_parameter_values(values, True)
            


       
