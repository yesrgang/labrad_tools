import json
from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter
from lib.pid import Dither, DitherPIID, DitherPID

class DitherLock(ConductorParameter):
    priority = 10
    def __init__(self, config):
        super(DitherLock, self).__init__(config)
        #self.pid = {lock_name: DitherPIID(**lock_conf['pid']) 
        self.pid = {lock_name: DitherPID(**lock_conf['pid']) 
            for lock_name, lock_conf in config.items()}
        self.dither = {lock_name: Dither(**lock_conf['dither']) 
            for lock_name, lock_conf in config.items()}
        self._value = {}

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
#        yield self.cxn.yesr10_andor.select_device('ikon')

    @inlineCallbacks
    def update(self):
        """ sefl.value == {
            'dither': [dither_name, side],
            'pid': [pid_name, side],
        }
        """
        current_value = self.value.copy()
        pid_value = current_value.get('pid')
        if pid_value:
            name = pid_value[0]
            side = pid_value[1]
            readout_type = self.pid[name].readout_type
            if readout_type == 'pmt':
                try:
                    frac = self.conductor.data['pico']['frac'][-1]
                except Exception as e:
                    print e
                    frac = None

            elif readout_type == 'camera':
                try:
                    image_path = self.conductor.data['andor']['image_path'][-1]
                    print 
                    print 'pid: ', name, side
                    print 'image_path', image_path
                    print 
                    camera_settings = self.pid[name].camera_settings
                    camera_settings.update({'image_path': image_path})
                    response = yield self.cxn.yesr10_andor.get_sums(
                        json.dumps(camera_settings)
                        )
                    frac = json.loads(response)['center']['frac']
                    tot = json.loads(response)['center']['tot']
                    yield self.conductor.set_parameter_value(
                            'andor', 'frac', frac, True)
                    yield self.conductor.set_parameter_value(
                            'andor', 'tot', tot, True)
                except Exception as e:
                    print e
                    print 'error getting frac from camera'
                    frac = None

            if frac:
                out = self.pid[name].tick(side, frac)
            else:
                out = self.pid[name].output
            yield self.conductor.set_parameter_value(name, 'frequency', out, True)
        
        dither_value = current_value.get('dither')
        if dither_value:
            name = dither_value[0]
            side = dither_value[1]

#            print 
#            print 'dither: ', name, side
#            print 

            center = self.pid[name].output
            out = self.dither[name].tick(side, center)
            yield self.conductor.set_parameter_value('clock_aom', 'center_frequency', center)
            yield self.conductor.set_parameter_value('clock_aom', 'frequency', out)

