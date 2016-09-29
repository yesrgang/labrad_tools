"""
### BEGIN NODE INFO
[info]
name = okfpga
version = 1.0
description = 
instancename = %LABRADNODE%_okfpga

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import json
import numpy as np
import os

import ok
from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

SEP = os.path.sep

class OKFPGAServer(LabradServer):
    name = '%LABRADNODE%_okfpga'
    @setting(1, device_id='s', returns='b')
    def open(self, c, device_id):
        c['device_id'] = device_id
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "found {} unused devices".format(module_count)
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            iden = tmp.GetDeviceID()
            if iden == device_id:
                c['xem'] = tmp
                print 'connected to {}'.format(iden)
                c['xem'].LoadDefaultPLLConfiguration() 
                return True
        return False

    @setting(2, returns='b')
    def close(self, c):
        if c.has_key('xem'):
            xem = c.pop('xem')
        return True
    
    @setting(3, filename='s')
    def program_bitfile(self, c, filename):
        error = c['xem'].ConfigureFPGA('bit_files'+SEP+filename)
        if error:
            print "unable to program sequencer"
            return False
        return True
    
    @setting(11, wire='i', byte_array='*i', returns='b')
    def write_to_pipe_in(self, c, wire, byte_array):
        print '{} piping in sequence to {}'.format(c['device_id'], wire)
        yield deferToThread(c['xem'].WriteToPipeInThr, wire, bytearray(byte_array))
        returnValue(True)

    @setting(12, wire='i', value='i')
    def set_wire_in(self, c, wire, value):
        print 'setting {} wire {} to {}'.format(c['device_id'], wire, value)
        c['xem'].SetWireInValue(wire, value)
    
    @setting(13)
    def update_wire_ins(self, c):
        c['xem'].UpdateWireIns()

if __name__ == "__main__":
    from labrad import util
    util.runServer(OKFPGAServer())
