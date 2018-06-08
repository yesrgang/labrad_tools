"""
### BEGIN NODE INFO
[info]
name = picoscope
version = 1.1
description = 
instancename = %LABRADNODE%_picoscope

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 947659321
timeout = 20
### END NODE INFO
"""
import h5py
import json
from labrad.server import LabradServer
from labrad.server import setting
import os
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import  returnValue

from picoscope import ps3000a

from server_tools.hardware_interface_server import HardwareInterfaceServer

from twisted.internet.defer import Deferred
from twisted.internet.reactor import callLater

def async_sleep(secs):
    d = Deferred()
    callLater(secs, d.callback, None)
    return d

class PicoscopeServer(HardwareInterfaceServer):
    """Provides access to picoscopes """
    name = '%LABRADNODE%_picoscope'
    
    def refresh_available_interfaces(self):
        ps = ps3000a.PS3000a(connect=False)
        
        try:
            serial_numbers = ps.enumerateUnits()
        except:
            serial_numbers = []
        
        additions = set(serial_numbers) - set(self.interfaces.keys())
        for sn in additions:
            inst = ps3000a.PS3000a(sn)
            self.interfaces[sn] = inst

        ps.close()

    @setting(3, channel='s', coupling='s', voltage_range='v', attenuation='i', enabled='b')
    def set_channel(self, c, channel, coupling, voltage_range, attenuation, enabled):
        ps = self.get_interface(c)
        ps.setChannel(channel, coupling=coupling, VRange=voltage_range,
            probeAttenuation=attenuation, enabled=enabled)

    @setting(4, duration='v', frequency='v')
    def set_sampling_frequency(self, c, duration, frequency):
        X = frequency
        Y = duration * frequency
        ps = self.get_interface(c)
        ans = ps.setSamplingFrequency(X, int(Y))
        print 'sampling @ {} MHz, {} damples'.format(ans[0] / Y, ans[1])

    @setting(5, source='s', threshold='v', timeout='i')
    def set_simple_trigger(self, c, source, threshold, timeout):
        """ 
        ARGS:
            source: 'External' for external trigger
            threshold: voltage for trigger threshold
            timeout: time in ms for timeout. use negative number for infinite wait.
        """
        ps = self.get_interface(c)
        ps.setSimpleTrigger(trigSrc=source, threshold_V=threshold, timeout_ms=timeout)

    @setting(6, n_segments='i', returns='i')
    def memory_segments(self, c, n_segments):
        ps = self.get_interface(c)
        samples_per_segment = ps.memorySegments(n_segments)
        return samples_per_segment

    @setting(7, n_captures='i')
    def set_no_of_captures(self, c, n_captures):
        ps = self.get_interface(c)
        ps.setNoOfCaptures(n_captures)

    @setting(8)
    def run_block(self, c):
        ps = self.get_interface(c)
        ps.runBlock()
    
#    @setting(9, data_path='s', data_format_json='s')
#    def save_data(self, c, data_path, data_format_json):
#        """
#        ARGS:
#            data_path: (string) location of data to be saved, relative to data_dir.
#            data_format: json dumped dict
#                data_format = {
#                    channel: {
#                        segment_name: 
#                            segment_number
#                        }
#                    }
#        RETURNS:
#            None
#        """
#        ps = self.get_interface(c)
#        data_format = json.loads(data_format_json)
#        callInThread(self.do_save_data, ps, data_path, data_format)

    def do_save_data(self, ps, data_path, data_format):
        while not ps.isReady():
            sleep(0.05)
        response = {}
        data = {}
        for channel, segments in data_format.items():
            data[channel] = {name: ps.getDataV(channel, 50000, segmentIndex=num)
                for name, num in segments.items()}

#        json.dump(response, data_path, default=lambda x: x.tolist())

        data_directory = DATADIR + os.path.dirname(data_path) 
        if not os.path.exists(directory):
            os.makedirs(directory)

        with h5py.File(DATADIR + data_path) as h5f:
            for channel, segments in data.items():
                grp = h5f.create_group(channel)
                for name, data in segments.items():
                    grp.create_dataset(name, data=data, compression='gzip')

    @setting(10, data_format='s', do_wait='b')
    def get_data(self, c, data_format, do_wait=False):
        ps = self.get_interface(c)
        while not ps.isReady():
            if not do_wait:
                message = 'picoscope ({}) is not ready'.format(c['address'])
                raise Exception(message)
            else:
                yield async_sleep(0.1)

        data_format = json.loads(data_format)
        response = {}
        for channel, segments in data_format.items():
            response[channel] = {}
            for label, i in segments.items():
                response[channel][label] =  ps.getDataV(channel, 50000, segmentIndex=i)

        returnValue(json.dumps(response, default=lambda x: x.tolist()))

__server__ = PicoscopeServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
