from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callInThread
from lib.andor import Andor
from lib.helpers import import_recorder

from server_tools.device_server import DeviceWrapper
    
    
class Ikon(DeviceWrapper):

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
        self.cam.SetEMCCDGain(self.emccd_gain)
        
    def record(self, record_name, record_type, recorder_config='{}'):
        Recorder = import_recorder(record_type)
        recorder = Recorder(recorder_config)
        callInThread(recorder.record, self.cam, record_name)

