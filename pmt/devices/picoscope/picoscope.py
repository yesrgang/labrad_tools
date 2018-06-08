from collections import deque
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from server_tools.device_server import Device

class Picoscope(Device):
    picoscope_server_name = None
    picoscope_serial_number = None
    picoscope_duration = None
    picoscope_frequency = None
    picoscope_n_capture = None
    picoscope_trigger_threshold = None # [V]
    picoscope_timeout = None # [ms]

    records = {}
    record_names = deque([])
    max_records = 100
    
    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.picoscope_server = yield self.cxn[self.picoscope_server_name]
        yield self.picoscope_server.select_interface(self.picoscope_serial_number)
        for channel, settings in self.picoscope_channel_settings.items():
            yield self.picoscope_server.set_channel(channel, settings['coupling'], 
                settings['voltage_range'], settings['attenuation'], settings['enabled'])
        
        yield self.picoscope_server.set_sampling_frequency(self.picoscope_duration, 
            self.picoscope_frequency)
        yield self.picoscope_server.set_simple_trigger('External', 
            self.picoscope_trigger_threshold, self.picoscope_timeout)
        _ = yield self.picoscope_server.memory_segments(self.picoscope_n_capture)
        yield self.picoscope_server.set_no_of_captures(self.picoscope_n_capture)

    @inlineCallbacks
    def record(self, data_path):
        yield None

    @inlineCallbacks
    def retrive(self, record_name, process_name):
        yield None
