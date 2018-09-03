from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callInThread

from server_tools.device_server import Device
    
from lib.andor import Andor
from lib.helpers import import_recorder, import_processor
    
class Ikon(Device):
    # 0 = high, 1 = low, 2 = off
    fan_mode = None
    
    # min is -80
    temperature = None
    
    # ?, set to 0
    cooler_mode = None

    # 1 = on, 0 = off
    cooler_on = None

    # ?, set to 4 for image
    read_mode = None

    # ?, set to 1
    shutter_type = None

    # ?, set to 0
    shutter_mode = None

    shutter_closing_time = None
    shutter_opening_time = None

    # 1 = external, 0 = internal
    trigger_mode = None

    accumulation_cycle_time = None
    number_accumulations = None
    kinetic_cycle_time = None
    pre_amp_gain = None
    hs_speed_type = None
    hs_speed_index = None
    vs_speed_index = None

    @inlineCallbacks
    def initialize(self):
        yield None
        self.cam = Andor()
        self.cam.SetFanMode(self.fan_mode)
        self.cam.SetTemperature(self.temperature)
        self.cam.SetCoolerMode(self.cooler_mode)
        if self.cooler_on:
            self.cam.CoolerON()
        else:
            self.cam.CoolerOFF()
        self.cam.SetReadMode(self.read_mode)
        self.cam.SetShutter(self.shutter_type, self.shutter_mode, 
                self.shutter_closing_time, self.shutter_opening_time)
        self.cam.SetTriggerMode(self.trigger_mode)
        self.cam.SetAccumulationCycleTime(self.accumulation_cycle_time)
        self.cam.SetNumberAccumulations(self.number_accumulations)
        self.cam.SetKineticCycleTime(self.kinetic_cycle_time)
        self.cam.SetPreAmpGain(self.pre_amp_gain)
        self.cam.SetHSSpeed(self.hs_speed_type, self.hs_speed_index)
        self.cam.SetVSSpeed(self.vs_speed_index)
        
    def record(self, record_path, record_type, recorder_config):
        print recorder_config
        if record_path and record_type:
            Recorder = import_recorder(record_type)
            recorder = Recorder(recorder_config)
            callInThread(recorder.record, self, record_path)
    
    def process(self, record_path, processor_type, processor_config):
        if processor_type:
            Processor = import_processor(processor_type)
            processor = Processor(processor_config)
            return processor.process(record_path)
